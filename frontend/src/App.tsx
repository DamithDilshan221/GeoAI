import { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';
import { SearchProvider } from './context/SearchContext';
import { AppShell } from './components/layout/AppShell';
import { CategorySelectionPage } from './pages/CategorySelectionPage';
import { NearbyFacilitiesPage } from './pages/NearbyFacilitiesPage';
import { FacilityDetailsPage } from './pages/FacilityDetailsPage';
import { RecommendationResultPage } from './pages/RecommendationResultPage';
import { SavedView } from './pages/SavedView';
import { SettingsView } from './pages/SettingsView';

export default function App() {
  useEffect(() => {
    document.body.classList.add('day');
  }, []);

  return (
    <SearchProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<CategorySelectionPage />} />
          <Route path="/nearby" element={<NearbyFacilitiesPage />} />
          <Route path="/facilities/:id" element={<FacilityDetailsPage />} />
          <Route path="/recommend" element={<RecommendationResultPage />} />
          <Route path="/saved" element={<SavedView />} />
          <Route path="/settings" element={<SettingsView />} />
        </Routes>
      </AppShell>
    </SearchProvider>
  );
}
