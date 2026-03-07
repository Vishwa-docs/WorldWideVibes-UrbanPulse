import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { Property, IncidentNearby, ServiceRequest311, MostVisitedLocation, VacantPropertyReport, BusinessLicense } from '../../types';
import { fetch311Requests, fetchMostVisited, fetchVacantPropertyReports, fetchBusinessLicenses } from '../../services/api';

const MONTGOMERY_CENTER: [number, number] = [32.3668, -86.3];

interface MapViewProps {
  properties: Property[];
  selectedProperty?: Property | null;
  onSelectProperty?: (property: Property) => void;
  layers?: Record<string, boolean>;
  incidents?: IncidentNearby[];
  showEquityOverlay?: boolean;
}

function markerColor(property: Property): string {
  if (property.is_vacant) return '#ef4444';
  if (property.is_city_owned) return '#3b82f6';
  if (property.property_type === 'commercial') return '#10b981';
  return '#9ca3af';
}

function scoreRadius(property: Property): number {
  const score = property.score?.overall_score;
  if (score == null) return 6;
  return Math.max(5, Math.min(14, score * 1.4));
}

function shouldShow(property: Property, layers?: Record<string, boolean>): boolean {
  if (!layers) return true;
  if (property.is_vacant && layers.vacant === false) return false;
  if (property.is_city_owned && layers.city_owned === false) return false;
  if (property.property_type === 'commercial' && layers.commercial === false) return false;
  return true;
}

function FlyTo({ property }: { property: Property | null | undefined }) {
  const map = useMap();
  useEffect(() => {
    if (property) {
      map.flyTo([property.latitude, property.longitude], 15, { duration: 0.8 });
    }
  }, [property, map]);
  return null;
}

function scoreLabel(score: number | undefined): string {
  if (score == null) return 'N/A';
  return score.toFixed(1);
}

function scoreBadgeColor(score: number | undefined): string {
  if (score == null) return 'bg-gray-100 text-gray-600';
  if (score >= 7) return 'bg-emerald-100 text-emerald-700';
  if (score >= 4) return 'bg-amber-100 text-amber-700';
  return 'bg-red-100 text-red-700';
}

export default function MapView({
  properties,
  selectedProperty,
  onSelectProperty,
  layers,
  incidents,
}: MapViewProps) {
  const showIncidents = layers?.incidents !== false;

  // ── Montgomery open data layers ────────────────────────────────────
  const [requests311, setRequests311] = useState<ServiceRequest311[]>([]);
  const [mostVisited, setMostVisited] = useState<MostVisitedLocation[]>([]);
  const [vacantReports, setVacantReports] = useState<VacantPropertyReport[]>([]);
  const [businesses, setBusinesses] = useState<BusinessLicense[]>([]);

  // Fetch data layers on demand when toggled on
  useEffect(() => {
    if (layers?.service_requests && requests311.length === 0) {
      fetch311Requests(300).then(d => setRequests311(d.items)).catch(() => {});
    }
  }, [layers?.service_requests]);

  useEffect(() => {
    if (layers?.foot_traffic && mostVisited.length === 0) {
      fetchMostVisited(300).then(d => setMostVisited(d.items)).catch(() => {});
    }
  }, [layers?.foot_traffic]);

  useEffect(() => {
    if (layers?.vacant_reports && vacantReports.length === 0) {
      fetchVacantPropertyReports(300).then(d => setVacantReports(d.items)).catch(() => {});
    }
  }, [layers?.vacant_reports]);

  useEffect(() => {
    if (layers?.business_licenses && businesses.length === 0) {
      fetchBusinessLicenses(300).then(d => setBusinesses(d.items)).catch(() => {});
    }
  }, [layers?.business_licenses]);

  return (
    <div className="h-full w-full relative">
      <MapContainer
        center={MONTGOMERY_CENTER}
        zoom={13}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FlyTo property={selectedProperty} />

        {properties
          .filter((p) => shouldShow(p, layers))
          .map((property) => {
            const isSelected = selectedProperty?.id === property.id;
            return (
              <CircleMarker
                key={property.id}
                center={[property.latitude, property.longitude]}
                radius={isSelected ? scoreRadius(property) + 3 : scoreRadius(property)}
                pathOptions={{
                  color: isSelected ? '#4f46e5' : markerColor(property),
                  fillColor: markerColor(property),
                  fillOpacity: isSelected ? 0.9 : 0.7,
                  weight: isSelected ? 3 : 1.5,
                }}
                eventHandlers={{
                  click: () => onSelectProperty?.(property),
                }}
              >
                <Popup>
                  <div className="min-w-[180px]">
                    <p className="font-semibold text-gray-900 text-sm mb-1">{property.address}</p>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-500">{property.property_type.replace('_', ' ')}</span>
                      {property.is_vacant && (
                        <span className="text-[10px] font-medium bg-red-100 text-red-700 px-1 rounded">Vacant</span>
                      )}
                      {property.is_city_owned && (
                        <span className="text-[10px] font-medium bg-blue-100 text-blue-700 px-1 rounded">City</span>
                      )}
                    </div>
                    {property.neighborhood && (
                      <p className="text-xs text-gray-400 mb-1">{property.neighborhood}</p>
                    )}
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className="text-xs text-gray-500">Score:</span>
                      <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${scoreBadgeColor(property.score?.overall_score)}`}>
                        {scoreLabel(property.score?.overall_score)}
                      </span>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

        {/* Incident markers */}
        {showIncidents &&
          incidents?.map((inc) => (
            <CircleMarker
              key={`inc-${inc.id}`}
              center={[inc.latitude, inc.longitude]}
              radius={4}
              pathOptions={{
                color: '#f97316',
                fillColor: '#f97316',
                fillOpacity: 0.5,
                weight: 1,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-medium">{inc.incident_type}</p>
                  {inc.severity && <p className="text-gray-500">Severity: {inc.severity}</p>}
                </div>
              </Popup>
            </CircleMarker>
          ))}

        {/* 311 Service Requests layer */}
        {layers?.service_requests &&
          requests311.map((req) => (
            <CircleMarker
              key={`311-${req.id}`}
              center={[req.latitude, req.longitude]}
              radius={5}
              pathOptions={{
                color: '#f59e0b',
                fillColor: '#f59e0b',
                fillOpacity: 0.6,
                weight: 1,
              }}
            >
              <Popup>
                <div className="text-xs min-w-[160px]">
                  <p className="font-semibold text-amber-700 mb-0.5">311 Request</p>
                  <p className="font-medium">{req.category}</p>
                  {req.description && <p className="text-gray-500 mt-0.5">{req.description.slice(0, 80)}</p>}
                  {req.address && <p className="text-gray-400 mt-0.5">{req.address}</p>}
                  <p className="text-[10px] text-gray-400 mt-1">Status: {req.status || 'Unknown'}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}

        {/* Most Visited / Foot Traffic layer */}
        {layers?.foot_traffic &&
          mostVisited.map((loc) => (
            <CircleMarker
              key={`visited-${loc.id}`}
              center={[loc.latitude, loc.longitude]}
              radius={Math.max(6, Math.min(16, Math.sqrt(loc.visits || 1) * 0.5))}
              pathOptions={{
                color: '#8b5cf6',
                fillColor: '#8b5cf6',
                fillOpacity: 0.5,
                weight: 2,
              }}
            >
              <Popup>
                <div className="text-xs min-w-[160px]">
                  <p className="font-semibold text-purple-700 mb-0.5">📍 Popular Location</p>
                  <p className="font-medium">{loc.name}</p>
                  {loc.category && <p className="text-gray-500">{loc.category}</p>}
                  <div className="flex gap-3 mt-1">
                    <span className="text-purple-600 font-bold">{(loc.visits || 0).toLocaleString()} visits</span>
                    <span className="text-gray-400">{(loc.visitors || 0).toLocaleString()} visitors</span>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}

        {/* Vacant Property Reports layer */}
        {layers?.vacant_reports &&
          vacantReports.map((vr) => (
            <CircleMarker
              key={`vacant-rpt-${vr.id}`}
              center={[vr.latitude, vr.longitude]}
              radius={6}
              pathOptions={{
                color: '#dc2626',
                fillColor: '#fca5a5',
                fillOpacity: 0.7,
                weight: 2,
                dashArray: '4 2',
              }}
            >
              <Popup>
                <div className="text-xs min-w-[160px]">
                  <p className="font-semibold text-red-700 mb-0.5">🏚️ Vacant/Blight Report</p>
                  <p className="font-medium">{vr.category}</p>
                  {vr.description && <p className="text-gray-500 mt-0.5">{vr.description.slice(0, 80)}</p>}
                  {vr.address && <p className="text-gray-400 mt-0.5">{vr.address}</p>}
                </div>
              </Popup>
            </CircleMarker>
          ))}

        {/* Business Licenses layer */}
        {layers?.business_licenses &&
          businesses.map((biz) => (
            <CircleMarker
              key={`biz-${biz.id}`}
              center={[biz.latitude, biz.longitude]}
              radius={5}
              pathOptions={{
                color: '#059669',
                fillColor: '#34d399',
                fillOpacity: 0.6,
                weight: 1.5,
              }}
            >
              <Popup>
                <div className="text-xs min-w-[160px]">
                  <p className="font-semibold text-emerald-700 mb-0.5">🏢 Licensed Business</p>
                  <p className="font-medium">{biz.business_name}</p>
                  {biz.business_type && <p className="text-gray-500">{biz.business_type}</p>}
                  {biz.address && <p className="text-gray-400 mt-0.5">{biz.address}</p>}
                </div>
              </Popup>
            </CircleMarker>
          ))}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur rounded-lg shadow-lg border border-gray-200 px-3 py-2 z-[1000]">
        <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Legend</p>
        <div className="space-y-1">
          {[
            { color: 'bg-red-500', label: 'Vacant' },
            { color: 'bg-blue-500', label: 'City-Owned' },
            { color: 'bg-green-500', label: 'Commercial' },
            { color: 'bg-gray-400', label: 'Other' },
            ...(layers?.service_requests ? [{ color: 'bg-amber-500', label: '311 Requests' }] : []),
            ...(layers?.foot_traffic ? [{ color: 'bg-purple-500', label: 'Foot Traffic' }] : []),
            ...(layers?.vacant_reports ? [{ color: 'bg-red-300', label: 'Vacant Reports' }] : []),
            ...(layers?.business_licenses ? [{ color: 'bg-emerald-400', label: 'Businesses' }] : []),
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
              <span className="text-[11px] text-gray-600">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
