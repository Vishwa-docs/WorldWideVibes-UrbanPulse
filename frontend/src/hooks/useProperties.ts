import { useState, useEffect, useCallback } from 'react';
import { fetchProperties, fetchRankedList, computeScores } from '../services/api';
import type { Property, RankedPropertyItem, PersonaType, ScenarioType } from '../types';

export function useProperties(persona: PersonaType, scenario: ScenarioType) {
  const [properties, setProperties] = useState<Property[]>([]);
  const [ranked, setRanked] = useState<RankedPropertyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [props, rankedData] = await Promise.all([
        fetchProperties({ limit: 100 }),
        fetchRankedList({ scenario, persona, limit: 50 }),
      ]);
      setProperties(props);
      setRanked(rankedData.items || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load properties');
    } finally {
      setLoading(false);
    }
  }, [persona, scenario]);

  useEffect(() => { load(); }, [load]);

  const recompute = useCallback(async () => {
    setLoading(true);
    try {
      await computeScores(scenario, persona);
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to recompute scores');
    } finally {
      setLoading(false);
    }
  }, [scenario, persona, load]);

  return { properties, ranked, loading, error, reload: load, recompute };
}
