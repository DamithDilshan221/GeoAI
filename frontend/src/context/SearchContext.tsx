/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface LocationData {
  lat: number;
  lon: number;
  accuracy: number;
}

interface SearchState {
  selectedCategory: string | null;
  accessibleOnly: boolean;
  location: LocationData | null;
  locationStatus: 'idle' | 'requesting' | 'granted' | 'denied' | 'unavailable';
}

type SearchAction =
  | { type: 'SET_CATEGORY'; payload: string }
  | { type: 'SET_ACCESSIBLE_ONLY'; payload: boolean }
  | { type: 'SET_LOCATION_STATUS'; payload: SearchState['locationStatus'] }
  | { type: 'SET_LOCATION'; payload: { location: LocationData; status: 'granted' } };

const initialState: SearchState = {
  selectedCategory: null,
  accessibleOnly: false,
  location: null,
  locationStatus: 'idle',
};

function searchReducer(state: SearchState, action: SearchAction): SearchState {
  switch (action.type) {
    case 'SET_CATEGORY':
      return { ...state, selectedCategory: action.payload };
    case 'SET_ACCESSIBLE_ONLY':
      return { ...state, accessibleOnly: action.payload };
    case 'SET_LOCATION_STATUS':
      return { ...state, locationStatus: action.payload };
    case 'SET_LOCATION':
      return { ...state, location: action.payload.location, locationStatus: action.payload.status };
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
