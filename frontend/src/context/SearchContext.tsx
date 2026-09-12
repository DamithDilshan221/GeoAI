/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useReducer, type ReactNode } from 'react';

interface LocationData {
  lat: number;
  lon: number;
  accuracy: number;
}

export interface SavedFacility {
  id: number;
  name: string;
  category: string;
  status: string;
  distance_m?: number;
  rating: number | null;
  latitude?: number;
  longitude?: number;
  audience?: string;
}

export interface SearchState {
  selectedCategory: string | null;
  selectedAudience: 'VISITOR' | 'STAFF' | null;
  location: LocationData | null;
  locationStatus: 'idle' | 'requesting' | 'granted' | 'denied' | 'unavailable';
  savedFacilities: Record<number, SavedFacility>;
}

export type SearchAction =
  | { type: 'SET_CATEGORY'; payload: string }
  | { type: 'SET_AUDIENCE'; payload: 'VISITOR' | 'STAFF' | null }
  | { type: 'SET_LOCATION_STATUS'; payload: SearchState['locationStatus'] }
  | { type: 'SET_LOCATION'; payload: { location: LocationData; status: 'granted' } }
  | { type: 'TOGGLE_SAVED'; payload: SavedFacility };

const initialState: SearchState = {
  selectedCategory: null,
  selectedAudience: null,
  location: null,
  locationStatus: 'idle',
  savedFacilities: {},
};

function searchReducer(state: SearchState, action: SearchAction): SearchState {
  switch (action.type) {
    case 'SET_CATEGORY':
      return { ...state, selectedCategory: action.payload };
    case 'SET_AUDIENCE':
      return { ...state, selectedAudience: action.payload };
    case 'SET_LOCATION_STATUS':
      return { ...state, locationStatus: action.payload };
    case 'SET_LOCATION':
      return { ...state, location: action.payload.location, locationStatus: action.payload.status };
    case 'TOGGLE_SAVED': {
      const nextSaved = { ...state.savedFacilities };
      if (nextSaved[action.payload.id]) {
        delete nextSaved[action.payload.id];
      } else {
        nextSaved[action.payload.id] = action.payload;
      }
      return { ...state, savedFacilities: nextSaved };
    }
    default:
      return state;
  }
}

const SearchContext = createContext<{
  state: SearchState;
  dispatch: React.Dispatch<SearchAction>;
} | undefined>(undefined);

export function SearchProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(searchReducer, initialState);
  return (
    <SearchContext.Provider value={{ state, dispatch }}>
      {children}
    </SearchContext.Provider>
  );
}

export function useSearchContext() {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearchContext must be used within a SearchProvider');
  }
  return context;
}
