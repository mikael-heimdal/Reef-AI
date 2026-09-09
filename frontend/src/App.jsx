import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Droplets,
  Fish,
  FlaskConical,
  Gauge,
  Plus,
  RefreshCw,
  Server,
  Thermometer,
  Waves,
  Wifi,
  WifiOff
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState
} from "react";

const API_BASE = "/backend";

const METRIC_CONFIG = {
  temperature: {
    label: "Temperatur",
    unit: "°C",
    icon: Thermometer,
    color: "#ff9364",
    min: 24,
    max: 27
  },

  ph: {
    label: "pH",
    unit: "pH",
    icon: FlaskConical,
    color: "#5dd6ff",
    min: 7.8,
    max: 8.5
  },

  kh: {
    label: "KH",
    unit: "dKH",
    icon: Gauge,
    color: "#9b8cff",
    min: 7,
    max: 9
  },

  salinity: {
    label: "Salinitet",
    unit: "ppt",
    icon: Droplets,
    color: "#4ce0b3",
    min: 33,
    max: 36
  },

  orp: {
    label: "Redox",
    unit: "mV",
    icon: Activity,
    color: "#f9d65c",
    min: 250,
    max: 450
  },

  redox: {
    label: "Redox",
    unit: "mV",
    icon: Activity,
    color: "#f9d65c",
    min: 250,
    max: 450
  },

  conductivity: {
    label: "Konduktivitet",
    unit: "mS/cm",
    icon: Waves,
    color: "#5da9ff",
    min: 45,
    max: 60
  }
};

const DEFAULT_VALUES = {
  temperature: null,
  ph: null,
  kh: null,
  salinity: null,
  orp: null
};

function normaliseMetric(metric) {
  return String(metric || "")
    .trim()
    .toLowerCase();
}

function formatValue(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "--";
  }

  const number = Number(value);

  if (Math.abs(number) >= 100) {
    return number.toFixed(0);
  }

  return number.toFixed(2);
}

function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "Ingen mätning";
  }

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return new Intl.DateTimeFormat(
    "sv-SE",
    {
      dateStyle: "short",
      timeStyle: "medium"
    }
  ).format(date);
}

function getMetricStatus(metric, value) {
  const config = METRIC_CONFIG[metric];

  if (
    !config ||
    value === null ||
    value === undefined
  ) {
    return {
      state: "unknown",
      label: "Ingen data"
    };
  }

  const number = Number(value);

  if (
    number < config.min ||
    number > config.max
  ) {
    return {
      state: "warning",
      label: "Kontrollera"
    };
  }

  return {
    state: "good",
    label: "Stabil"
  };
}

function MetricCard({
  metric,
  measurement
}) {
  const config =
    METRIC_CONFIG[metric] ||
    {
      label: metric,
      unit: measurement?.unit || "",
      icon: Activity,
      color: "#5dd6ff"
    };

  const Icon = config.icon;
  const value = measurement?.value ?? null;

  const status = getMetricStatus(
    metric,
    value
  );

  return (
    <article
      className={`metric-card ${status.state}`}
      style={{
        "--metric-color": config.color
      }}
    >
      <div className="metric-header">
        <div className="metric-icon">
          <Icon size={21} />
        </div>

        <span className={`status-badge ${status.state}`}>
          {status.label}
        </span>
      </div>

      <div className="metric-label">
        {config.label}
      </div>

      <div className="metric-value-row">
        <strong className="metric-value">
          {formatValue(value)}
        </strong>

        <span className="metric-unit">
          {measurement?.unit || config.unit}
        </span>
      </div>

      <div className="metric-time">
        {formatTimestamp(
          measurement?.timestamp ||
          measurement?.measured_at
        )}
      </div>
    </article>
  );
}

function LineChart({
  title,
  metric,
  measurements
}) {
  const config =
    METRIC_CONFIG[metric] ||
    {
      label: metric,
      color: "#5dd6ff",
      unit: ""
    };

  const values = measurements
    .filter(
      (item) =>
        normaliseMetric(item.metric) === metric
    )
    .slice()
    .reverse()
    .slice(-30);

  const numericValues = values
    .map((item) => Number(item.value))
    .filter((value) => Number.isFinite(value));

  const hasData = numericValues.length > 0;

  const minimum = hasData
    ? Math.min(...numericValues)
    : 0;

  const maximum = hasData
    ? Math.max(...numericValues)
    : 1;

  const range = maximum - minimum || 1;

  const width = 700;
  const height = 230;
  const padding = 24;

  const points = values
    .map((item, index) => {
      const value = Number(item.value);

      const x =
        values.length <= 1
          ? width / 2
          : padding +
            (
              index /
              (values.length - 1)
            ) *
            (width - padding * 2);

      const y =
        height -
        padding -
        (
          (value - minimum) /
          range
        ) *
        (height - padding * 2);

      return `${x},${y}`;
    })
    .join(" ");

  return (
    <article className="chart-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">
            Historik
          </span>

          <h2>{title}</h2>
        </div>

        <div className="chart-current">
          {hasData
            ? `${formatValue(
                numericValues[
                  numericValues.length - 1
                ]
              )} ${config.unit}`
            : "Ingen data"}
        </div>
      </div>

      {!hasData ? (
        <div className="empty-chart">
          <Activity size={32} />

          <span>
            Lägg in mätvärden för att visa trend
          </span>
        </div>
      ) : (
        <>
          <div className="chart-range">
            <span>
              Max {formatValue(maximum)}
            </span>

            <span>
              Min {formatValue(minimum)}
            </span>
          </div>

          <div className="chart-wrapper">
            <svg
              viewBox={`0 0 ${width} ${height}`}
              preserveAspectRatio="none"
              className="line-chart"
              aria-label={`${title} trend`}
            >
              <defs>
                <linearGradient
                  id={`gradient-${metric}`}
                  x1="0"
                  x2="0"
                  y1="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor={config.color}
                    stopOpacity="0.36"
                  />

                  <stop
                    offset="100%"
                    stopColor={config.color}
                    stopOpacity="0"
                  />
                </linearGradient>
              </defs>

              {[1, 2, 3, 4].map((line) => (
                <line
                  key={line}
                  x1="0"
                  x2={width}
                  y1={(height / 5) * line}
                  y2={(height / 5) * line}
                  className="grid-line"
                />
              ))}

              <polygon
                points={
                  `${padding},${height - padding} ` +
                  points +
                  ` ${width - padding},${height - padding}`
                }
                fill={`url(#gradient-${metric})`}
              />

              <polyline
                points={points}
                fill="none"
                stroke={config.color}
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
              />
            </svg>
          </div>
        </>
      )}
    </article>
  );
}

function AddMeasurement({
  onCreated
}) {
  const [form, setForm] = useState({
    metric: "kh",
    value: "",
    unit: "dKH"
  });

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState("");

  function updateMetric(metric) {
    const config =
      METRIC_CONFIG[metric];

    setForm({
      metric,
      value: "",
      unit: config?.unit || ""
    });
  }

  async function submit(event) {
    event.preventDefault();

    if (form.value === "") {
      setMessage("Ange ett mätvärde.");
      return;
    }

    setSaving(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_BASE}/measurements/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            metric: form.metric,
            value: Number(form.value),
            unit: form.unit
          })
        }
      );

      if (!response.ok) {
        const text = await response.text();

        throw new Error(
          text ||
          `HTTP ${response.status}`
        );
      }

      setForm((current) => ({
        ...current,
        value: ""
      }));

      setMessage("Mätvärdet sparades.");

      await onCreated();
    } catch (error) {
      setMessage(
        `Kunde inte spara: ${error.message}`
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <article className="form-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">
            Manuell registrering
          </span>

          <h2>Nytt mätvärde</h2>
        </div>

        <Plus size={22} />
      </div>

      <form
        className="measurement-form"
        onSubmit={submit}
      >
        <label>
          Parameter

          <select
            value={form.metric}
            onChange={(event) =>
              updateMetric(event.target.value)
            }
          >
            <option value="temperature">
              Temperatur
            </option>

            <option value="ph">
              pH
            </option>

            <option value="kh">
              KH
            </option>

            <option value="salinity">
              Salinitet
            </option>

            <option value="orp">
              Redox
            </option>
          </select>
        </label>

        <div className="form-row">
          <label>
            Värde

            <input
              type="number"
              inputMode="decimal"
              step="any"
              value={form.value}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  value: event.target.value
                }))
              }
              placeholder="8.10"
            />
          </label>

          <label>
            Enhet

            <input
              value={form.unit}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  unit: event.target.value
                }))
              }
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={saving}
        >
          {saving
            ? "Sparar..."
            : "Spara mätvärde"}
        </button>

        {message && (
          <p className="form-message">
            {message}
          </p>
        )}
      </form>
    </article>
  );
}

function RecentMeasurements({
  measurements
}) {
  return (
    <article className="table-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">
            Databas
          </span>

          <h2>Senaste mätvärden</h2>
        </div>

        <Database size={22} />
      </div>

      {measurements.length === 0 ? (
        <div className="empty-list">
          Inga mätvärden finns ännu.
        </div>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Värde</th>
                <th>Tidpunkt</th>
              </tr>
            </thead>

            <tbody>
              {measurements
                .slice(0, 12)
                .map((item) => {
                  const metric =
                    normaliseMetric(item.metric);

                  const config =
                    METRIC_CONFIG[metric];

                  return (
                    <tr key={item.id}>
                      <td>
                        <span
                          className="metric-dot"
                          style={{
                            background:
                              config?.color ||
                              "#5dd6ff"
                          }}
                        />

                        {config?.label ||
                          item.metric}
                      </td>

                      <td>
                        <strong>
                          {formatValue(
                            item.value
                          )}
                        </strong>{" "}
                        {item.unit}
                      </td>

                      <td>
                        {formatTimestamp(
                          item.timestamp ||
                          item.measured_at
                        )}
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}

function App() {
  const [measurements, setMeasurements] =
    useState([]);

  const [ghlStatus, setGhlStatus] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [lastRefresh, setLastRefresh] =
    useState(null);

  const loadDashboard =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const [
          measurementResponse,
          ghlResponse
        ] = await Promise.all([
          fetch(
            `${API_BASE}/measurements/`
          ),

          fetch(
            `${API_BASE}/ghl/status`
          )
        ]);

        if (!measurementResponse.ok) {
          throw new Error(
            `Measurements HTTP ${measurementResponse.status}`
          );
        }

        const measurementData =
          await measurementResponse.json();

        setMeasurements(
          Array.isArray(measurementData)
            ? measurementData
                .slice()
                .sort((a, b) => {
                  const timeA = new Date(
                    a.timestamp ||
                    a.measured_at ||
                    0
                  ).getTime();

                  const timeB = new Date(
                    b.timestamp ||
                    b.measured_at ||
                    0
                  ).getTime();

                  return timeB - timeA;
                })
            : []
        );

        if (ghlResponse.ok) {
          setGhlStatus(
            await ghlResponse.json()
          );
        } else {
          setGhlStatus({
            connected: false,
            message:
              `GHL HTTP ${ghlResponse.status}`
          });
        }

        setLastRefresh(new Date());
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    loadDashboard();

    const interval = window.setInterval(
      loadDashboard,
      30000
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [loadDashboard]);

  const latestByMetric =
    useMemo(() => {
      const latest = {
        ...DEFAULT_VALUES
      };

      for (const item of measurements) {
        const metric =
          normaliseMetric(item.metric);

        const normalisedMetric =
          metric === "redox"
            ? "orp"
            : metric;

        if (
          Object.prototype.hasOwnProperty.call(
            latest,
            normalisedMetric
          ) &&
          latest[normalisedMetric] === null
        ) {
          latest[normalisedMetric] = item;
        }
      }

      return latest;
    }, [measurements]);

  const connected =
    Boolean(ghlStatus?.connected);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Fish size={28} />
          </div>

          <div>
            <strong>Reef AI</strong>
            <span>Intelligent Reef System</span>
          </div>
        </div>

        <nav className="nav">
          <a href="#overview">
            <Gauge size={19} />
            Översikt
          </a>

          <a href="#history">
            <Activity size={19} />
            Historik
          </a>

          <a href="#ghl">
            <Server size={19} />
            ProfiLux
          </a>

          <a href="#measurements">
            <FlaskConical size={19} />
            Mätvärden
          </a>
        </nav>

        <div className="sidebar-footer">
          <div
            className={
              connected
                ? "connection good"
                : "connection offline"
            }
          >
            {connected ? (
              <Wifi size={18} />
            ) : (
              <WifiOff size={18} />
            )}

            <div>
              <strong>
                ProfiLux 3
              </strong>

              <span>
                {connected
                  ? "Ansluten"
                  : "Ej ansluten"}
              </span>
            </div>
          </div>

          <small>
            Reef AI Backend v0.3
          </small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">
              1500 L REVSYSTEM
            </span>

            <h1>Akvarieöversikt</h1>

            <p>
              GHL ProfiLux ansvarar för
              styrning. Reef AI analyserar
              och visualiserar informationen.
            </p>
          </div>

          <button
            type="button"
            className="refresh-button"
            onClick={loadDashboard}
            disabled={loading}
          >
            <RefreshCw
              size={18}
              className={
                loading ? "spinning" : ""
              }
            />

            Uppdatera
          </button>
        </header>

        {error && (
          <div className="error-banner">
            <AlertTriangle size={20} />

            <div>
              <strong>
                Backend kunde inte läsas
              </strong>

              <span>{error}</span>
            </div>
          </div>
        )}

        <section
          className="system-strip"
          id="ghl"
        >
          <div className="system-state">
            <div
              className={
                connected
                  ? "system-icon connected"
                  : "system-icon disconnected"
              }
            >
              {connected ? (
                <CheckCircle2 size={24} />
              ) : (
                <WifiOff size={24} />
              )}
            </div>

            <div>
              <span className="system-label">
                GHL ProfiLux 3
              </span>

              <strong>
                {connected
                  ? "Kommunikation aktiv"
                  : "Väntar på lokal anslutning"}
              </strong>
            </div>
          </div>

          <div className="system-detail">
            <span>Driftläge</span>

            <strong>
              {ghlStatus?.mode ||
                "Read-only"}
            </strong>
          </div>

          <div className="system-detail">
            <span>Datapunkter</span>

            <strong>
              {measurements.length}
            </strong>
          </div>

          <div className="system-detail">
            <span>Senast uppdaterad</span>

            <strong>
              {lastRefresh
                ? lastRefresh.toLocaleTimeString(
                    "sv-SE"
                  )
                : "--"}
            </strong>
          </div>
        </section>

        <section
          className="metrics-grid"
          id="overview"
        >
          {Object.keys(DEFAULT_VALUES)
            .map((metric) => (
              <MetricCard
                key={metric}
                metric={metric}
                measurement={
                  latestByMetric[metric]
                }
              />
            ))}
        </section>

        <section
          className="charts-grid"
          id="history"
        >
          <LineChart
            title="KH-trend"
            metric="kh"
            measurements={measurements}
          />

          <LineChart
            title="pH-trend"
            metric="ph"
            measurements={measurements}
          />

          <LineChart
            title="Temperaturtrend"
            metric="temperature"
            measurements={measurements}
          />

          <LineChart
            title="Salinitetstrend"
            metric="salinity"
            measurements={measurements}
          />
        </section>

        <section
          className="bottom-grid"
          id="measurements"
        >
          <AddMeasurement
            onCreated={loadDashboard}
          />

          <RecentMeasurements
            measurements={measurements}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
