import { useState, useEffect, useCallback } from 'react';
import { fetchWatchlist, addToWatchlist, removeFromWatchlist } from '../services/api';
import type { WatchlistItem, PersonaType } from '../types';

export function useWatchlist(persona: PersonaType) {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchWatchlist(persona);
      setItems(data.items || []);
    } catch {
      // silently fail for demo
    } finally {
      setLoading(false);
    }
  }, [persona]);

  useEffect(() => { load(); }, [load]);

  const add = useCallback(async (propertyId: number, notes?: string) => {
    try {
      await addToWatchlist(propertyId, persona, notes);
      await load();
    } catch (e) { console.error(e); }
  }, [persona, load]);

  const remove = useCallback(async (id: number) => {
    try {
      await removeFromWatchlist(id);
      await load();
    } catch (e) { console.error(e); }
  }, [load]);

  const isWatched = useCallback((propertyId: number) => {
    return items.some(item => item.property_id === propertyId);
  }, [items]);

  return { items, loading, add, remove, isWatched, reload: load };
}
