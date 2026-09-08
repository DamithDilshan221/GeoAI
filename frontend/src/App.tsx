import { Route, Routes } from 'react-router-dom';
import { SearchProvider } from './context/SearchContext';
import { AppShell } from './components/layout/AppShell';
import { CategorySelectionPage } from './pages/CategorySelectionPage';
import { NearbyFacilitiesPage } from './pages/NearbyFacilitiesPage';
import { FacilityDetailsPage } from './pages/FacilityDetailsPage';
import { RecommendationResultPage } from './pages/RecommendationResultPage';

export default function App() {
  return (
    <SearchProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<CategorySelectionPage />} />
          <Route path="/nearby" element={<NearbyFacilitiesPage />} />
          <Route path="/facilities/:id" element={<FacilityDetailsPage />} />
          <Route path="/recommend" element={<RecommendationResultPage />} />
        </Routes>
      </AppShell>
    </SearchProvider>
  );
}
