import { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, Snowflake, Wind, Droplets, Thermometer } from 'lucide-react';
import { fetchCurrentWeather, fetchWeatherForecast } from '../../services/api';
import type { WeatherCurrent, WeatherForecast } from '../../types';

function weatherIcon(code: number) {
  if (code === 0 || code === 1) return <Sun className="w-5 h-5 text-amber-500" />;
  if (code <= 3) return <Cloud className="w-5 h-5 text-gray-400" />;
  if (code >= 61 && code <= 67) return <CloudRain className="w-5 h-5 text-blue-500" />;
  if (code >= 71 && code <= 77) return <Snowflake className="w-5 h-5 text-blue-300" />;
  if (code >= 80 && code <= 82) return <CloudRain className="w-5 h-5 text-blue-600" />;
  if (code >= 95) return <CloudRain className="w-5 h-5 text-purple-600" />;
  return <Cloud className="w-5 h-5 text-gray-400" />;
}

export default function WeatherWidget() {
  const [current, setCurrent] = useState<WeatherCurrent | null>(null);
  const [forecast, setForecast] = useState<WeatherForecast | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchCurrentWeather().catch(() => null),
      fetchWeatherForecast().catch(() => null),
    ]).then(([c, f]) => {
      setCurrent(c);
      setForecast(f);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-32 mb-3" />
        <div className="h-8 bg-gray-200 rounded w-24 mb-2" />
        <div className="h-3 bg-gray-100 rounded w-full" />
      </div>
    );
  }

  if (!current && !forecast) return null;

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
      <div className="flex items-center gap-2 mb-3">
        <Thermometer className="w-4 h-4 text-orange-500" />
        <h3 className="text-sm font-semibold text-gray-800">Weather — Montgomery, AL</h3>
      </div>

      {current && (
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-2">
            {weatherIcon(current.weather_code)}
            <span className="text-3xl font-bold text-gray-900">{Math.round(current.temperature_f)}°F</span>
          </div>
          <div className="text-xs text-gray-500 space-y-0.5">
            <p className="font-medium text-gray-700">{current.weather_description}</p>
            <div className="flex items-center gap-1">
              <Droplets className="w-3 h-3" />
              <span>{current.humidity_pct}% humidity</span>
            </div>
            <div className="flex items-center gap-1">
              <Wind className="w-3 h-3" />
              <span>{current.wind_speed_mph} mph</span>
            </div>
          </div>
        </div>
      )}

      {forecast && forecast.forecast.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">7-Day Forecast</p>
          <div className="grid grid-cols-7 gap-1">
            {forecast.forecast.map((day) => {
              const d = new Date(day.date + 'T12:00:00');
              const label = dayNames[d.getDay()];
              return (
                <div key={day.date} className="text-center">
                  <p className="text-[10px] font-semibold text-gray-500 mb-1">{label}</p>
                  <div className="flex justify-center mb-0.5">
                    {weatherIcon(day.weather_code)}
                  </div>
                  <p className="text-xs font-bold text-gray-900">{Math.round(day.high_f)}°</p>
                  <p className="text-[10px] text-gray-400">{Math.round(day.low_f)}°</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {current && (
        <p className="text-[9px] text-gray-300 mt-2">
          {current.source} · {new Date(current.fetched_at).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
