from __future__ import annotations

import asyncio
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import httpx


class GHLConnectionError(RuntimeError):
    """ProfiLux kunde inte nås över nätverket."""


class GHLProtocolError(RuntimeError):
    """ProfiLux svarade, men svaret kunde inte tolkas."""


@dataclass(slots=True)
class GHLSensorDefinition:
    key: str
    name: str
    code: int
    unit: str
    decimals: int = 1
    enabled: bool = True


@dataclass(slots=True)
class GHLReading:
    metric: str
    name: str
    value: float
    unit: str
    code: int
    measured_at: datetime
    source: str
    raw_response: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["measured_at"] = self.measured_at.isoformat()
        return data


class GHLProfiLux3Service:
    """
    Read-only connector för ProfiLux 3:s lokala HTTP-gränssnitt.

    Endpoint:
        GET /communication.php?dir=enq&code=<numeric_code>

    Förväntat svar kan exempelvis innehålla:
        command=<code>&data=<value>

    Sensorernas numeriska koder är installations- och protokollspecifika.
    Lägg därför koderna i konfigurationen och verifiera dem mot den
    ProfiLux 3-installation som används.
    """

    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        port: int = 80,
        timeout_seconds: float = 8.0,
        verify_ssl: bool = False,
        use_https: bool = False,
        mock_mode: bool = False,
        sensors: list[GHLSensorDefinition] | None = None,
    ) -> None:
        clean_host = host.strip()

        if clean_host.startswith("http://"):
            clean_host = clean_host.removeprefix("http://")
        elif clean_host.startswith("https://"):
            clean_host = clean_host.removeprefix("https://")

        clean_host = clean_host.rstrip("/")

        if not clean_host:
            raise ValueError("GHL_HOST får inte vara tom")

        if not 1 <= port <= 65535:
            raise ValueError("GHL_PORT måste vara mellan 1 och 65535")

        self.host = clean_host
        self.username = username
        self.password = password
        self.port = port
        self.timeout_seconds = timeout_seconds
        self.verify_ssl = verify_ssl
        self.use_https = use_https
        self.mock_mode = mock_mode
        self.sensors = sensors or []

    @property
    def base_url(self) -> str:
        scheme = "https" if self.use_https else "http"

        default_port = 443 if self.use_https else 80
        port_suffix = "" if self.port == default_port else f":{self.port}"

        return f"{scheme}://{self.host}{port_suffix}"

    def _auth(self) -> httpx.BasicAuth | None:
        if not self.username:
            return None

        return httpx.BasicAuth(
            username=self.username,
            password=self.password or "",
        )

    async def _request_code(self, code: int) -> str:
        if code < 0:
            raise ValueError("GHL-koden får inte vara negativ")

        if self.mock_mode:
            return self._mock_response(code)

        url = f"{self.base_url}/communication.php"

        params = {
            "dir": "enq",
            "code": str(code),
        }

        try:
            async with httpx.AsyncClient(
                auth=self._auth(),
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={
                        "Accept": "text/plain, */*",
                        "User-Agent": "Reef-AI/0.3 ProfiLux3-ReadOnly",
                    },
                )

        except httpx.TimeoutException as exc:
            raise GHLConnectionError(
                f"Timeout vid anslutning till {self.base_url}"
            ) from exc

        except httpx.ConnectError as exc:
            raise GHLConnectionError(
                f"Kunde inte ansluta till {self.base_url}"
            ) from exc

        except httpx.HTTPError as exc:
            raise GHLConnectionError(
                f"HTTP-fel mot ProfiLux: {exc}"
            ) from exc

        if response.status_code == 401:
            raise GHLConnectionError(
                "ProfiLux nekade inloggningen. Kontrollera användarnamn och lösenord."
            )

        if response.status_code == 403:
            raise GHLConnectionError(
                "ProfiLux nekade åtkomst till communication.php."
            )

        if response.status_code == 404:
            raise GHLConnectionError(
                "communication.php hittades inte på ProfiLux."
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GHLConnectionError(
                f"ProfiLux svarade med HTTP {response.status_code}"
            ) from exc

        body = response.text.strip()

        if not body:
            raise GHLProtocolError(
                f"Tomt svar från ProfiLux för kod {code}"
            )

        return body

    @staticmethod
    def _extract_data_value(raw_response: str) -> str:
        patterns = (
            r"(?:^|[&;\s])data=([^&;\r\n]+)",
            r"<data>\s*([^<]+?)\s*</data>",
            r'"data"\s*:\s*"([^"]+)"',
            r'"data"\s*:\s*([-+]?\d+(?:[.,]\d+)?)',
        )

        for pattern in patterns:
            match = re.search(
                pattern,
                raw_response,
                flags=re.IGNORECASE,
            )

            if match:
                return match.group(1).strip()

        raise GHLProtocolError(
            f"Kunde inte hitta datafält i ProfiLux-svaret: {raw_response[:200]}"
        )

    @classmethod
    def _parse_numeric_value(
        cls,
        raw_response: str,
        decimals: int,
    ) -> float:
        data_value = cls._extract_data_value(raw_response)

        cleaned = (
            data_value
            .replace(",", ".")
            .replace(" ", "")
            .strip()
        )

        match = re.search(
            r"[-+]?\d+(?:\.\d+)?",
            cleaned,
        )

        if not match:
            raise GHLProtocolError(
                f"Datafältet innehåller inget numeriskt värde: {data_value}"
            )

        value_text = match.group(0)
        value = float(value_text)

        # Om controllern returnerar ett heltal används sensorskalningen.
        # Exempel: data=253 och decimals=1 blir 25.3.
        if "." not in value_text and decimals > 0:
            value = value / (10 ** decimals)

        return value

    async def read_sensor(
        self,
        sensor: GHLSensorDefinition,
    ) -> GHLReading:
        if not sensor.enabled:
            raise ValueError(
                f"Sensorn {sensor.key} är avstängd"
            )

        raw_response = await self._request_code(sensor.code)

        value = self._parse_numeric_value(
            raw_response=raw_response,
            decimals=sensor.decimals,
        )

        return GHLReading(
            metric=sensor.key,
            name=sensor.name,
            value=value,
            unit=sensor.unit,
            code=sensor.code,
            measured_at=datetime.now(timezone.utc),
            source="profilux3-mock" if self.mock_mode else "profilux3",
            raw_response=raw_response,
        )

    async def read_all_sensors(self) -> listenabled_sensors = [
            sensor
            for sensor in self.sensors
            if sensor.enabled
        ]

        if not enabled_sensors:
            return []

        results = await asyncio.gather(
            *[
                self.read_sensor(sensor)
                for sensor in enabled_sensors
            ],
            return_exceptions=True,
        )

        readings: list[GHLReading] = []
        errors: list[str] = []

        for sensor, result in zip(
            enabled_sensors,
            results,
            strict=True,
        ):
            if isinstance(result, Exception):
                errors.append(
                    f"{sensor.key}: {result}"
                )
            else:
                readings.append(result)

        if errors and not readings:
            raise GHLConnectionError(
                "Ingen GHL-sensor kunde läsas. "
                + " | ".join(errors)
            )

        return readings

    async def check_connection(self) -> dict[str, Any]:
        if self.mock_mode:
            return {
                "controller": "ProfiLux 3",
                "connected": True,
                "mode": "mock",
                "host": self.host,
                "base_url": self.base_url,
                "configured_sensors": len(self.sensors),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

        if not self.sensors:
            return {
                "controller": "ProfiLux 3",
                "connected": False,
                "mode": "http-read-only",
                "host": self.host,
                "base_url": self.base_url,
                "configured_sensors": 0,
                "message": "Ingen verifierad testkod är konfigurerad.",
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

        first_sensor = next(
            (
                sensor
                for sensor in self.sensors
                if sensor.enabled
            ),
            None,
        )

        if first_sensor is None:
            return {
                "controller": "ProfiLux 3",
                "connected": False,
                "mode": "http-read-only",
                "host": self.host,
                "base_url": self.base_url,
                "configured_sensors": len(self.sensors),
                "message": "Alla konfigurerade sensorer är avstängda.",
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

        try:
            reading = await self.read_sensor(first_sensor)

            return {
                "controller": "ProfiLux 3",
                "connected": True,
                "mode": "http-read-only",
                "host": self.host,
                "base_url": self.base_url,
                "test_metric": reading.metric,
                "test_value": reading.value,
                "test_unit": reading.unit,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

        except (GHLConnectionError, GHLProtocolError) as exc:
            return {
                "controller": "ProfiLux 3",
                "connected": False,
                "mode": "http-read-only",
                "host": self.host,
                "base_url": self.base_url,
                "error": str(exc),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

    @staticmethod
    def _mock_response(code: int) -> str:
        mock_values = {
            1: "command=1&data=253",
            2: "command=2&data=812",
            3: "command=3&data=381",
            4: "command=4&data=350",
            5: "command=5&data=81",
        }

        return mock_values.get(
            code,
            f"command={code}&data=0",
        )
