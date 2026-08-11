import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DatasetSidebar } from './components/DatasetSidebar';
import { DatasetOverview } from './components/DatasetOverview';
import { MetadataQualityCard } from './components/MetadataQualityCard';
import { MetadataGapList } from './components/MetadataGapList';
import { ReasoningPanel } from './components/ReasoningPanel';
import { ArtifactViewer } from './components/ArtifactViewer';
import { ValidationReportComponent } from './components/ValidationReport';
import { LineageGraph } from './components/LineageGraph';
import { PublishPanel } from './components/PublishPanel';
import { LoginPage } from './components/LoginPage';
import { LandingPage } from './components/LandingPage';
import { CustomCursor } from './components/CustomCursor';
import { DatasetDetail, DatasetSummary, GenerationResult } from './types';
import { fetchDatasetDetail, fetchDatasets, generateModel } from './api/client';
import { Database, AlertTriangle } from 'lucide-react';

export function App() {
  const [view, setView] = useState<'landing' | 'login' | 'dashboard'>('landing');

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return localStorage.getItem('forgehub_authenticated') === 'true';
  });
  const [username, setUsername] = useState<string>(() => {
    return localStorage.getItem('forgehub_username') || 'data.engineer@company.com';
  });

  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [datasetDetail, setDatasetDetail] = useState<DatasetDetail | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);
  const [loadingDatasets, setLoadingDatasets] = useState<boolean>(true);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isPublished, setIsPublished] = useState<boolean>(false);

  // Launch Studio trigger from Landing Page
  const handleLaunchStudio = () => {
    if (isAuthenticated) {
      setView('dashboard');
    } else {
      setView('login');
    }
  };

  // Handle User Login
  const handleLogin = (user: string, mode: 'demo' | 'live') => {
    localStorage.setItem('forgehub_authenticated', 'true');
    localStorage.setItem('forgehub_username', user);
    setUsername(user);
    setIsAuthenticated(true);
    setView('dashboard');
  };

  // Handle User Logout
  const handleLogout = () => {
    localStorage.removeItem('forgehub_authenticated');
    setIsAuthenticated(false);
    setView('landing');
  };

  // Fetch datasets upon dashboard view
  useEffect(() => {
    if (view !== 'dashboard') return;
    setLoadingDatasets(true);
    fetchDatasets()
      .then((data) => {
        setDatasets(data);
        if (data.length > 0 && !selectedId) {
          setSelectedId(data[0].id);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingDatasets(false));
  }, [view]);

  // Fetch dataset detail on select
  useEffect(() => {
    if (view !== 'dashboard' || !selectedId) return;
    setLoadingDetail(true);
    setGenerationResult(null);
    setIsPublished(false);
    setError(null);

    fetchDatasetDetail(selectedId)
      .then((detail) => setDatasetDetail(detail))
      .catch((err) => setError(err.message))
      .finally(() => setLoadingDetail(false));
  }, [selectedId, view]);

  // Handle model generation trigger
  const handleGenerate = async (brokenMode: boolean = false) => {
    if (!selectedId) return;
    setGenerating(true);
    setError(null);
    setIsPublished(false);

    try {
      const res = await generateModel(selectedId, brokenMode);
      setGenerationResult(res);
    } catch (err: any) {
      setError(err.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <>
      {/* Custom Classy & Comical Cursor */}
      <CustomCursor />

      {/* Render View based on state */}
      {view === 'landing' && (
        <LandingPage
          onStart={handleLaunchStudio}
          onSelectDataset={(id) => setSelectedId(id)}
        />
      )}

      {view === 'login' && (
        <LoginPage
          onLogin={handleLogin}
          onGoHome={() => setView('landing')}
        />
      )}

      {view === 'dashboard' && (
        <div className="min-h-screen bg-zinc-950 text-slate-100 flex flex-col font-sans comic-dots selection:bg-yellow-400 selection:text-black">
          {/* Top Navbar */}
          <Navbar
            demoMode={true}
            username={username}
            onLogout={handleLogout}
            onGoHome={() => setView('landing')}
          />

          <div className="flex flex-1">
            {/* Left Sidebar */}
            <DatasetSidebar
              datasets={datasets}
              selectedId={selectedId}
              onSelect={(id) => setSelectedId(id)}
              loading={loadingDatasets}
            />

            {/* Main Content Area */}
            <main className="flex-1 p-6 max-w-7xl mx-auto overflow-y-auto">
              {error && (
                <div className="p-4 rounded-2xl bg-red-600 text-white font-mono font-bold text-xs mb-6 flex items-center gap-2 border-3 border-black shadow-pop">
                  <AlertTriangle className="h-4 w-4 stroke-[3] shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {loadingDetail ? (
                <div className="space-y-6">
                  <div className="h-48 rounded-3xl bg-zinc-900 animate-pulse border-4 border-black shadow-pop" />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="h-64 rounded-3xl bg-zinc-900 animate-pulse border-4 border-black shadow-pop" />
                    <div className="h-64 rounded-3xl bg-zinc-900 animate-pulse border-4 border-black shadow-pop" />
                  </div>
                </div>
              ) : datasetDetail ? (
                <>
                  {/* Dataset Header Overview */}
                  <DatasetOverview
                    dataset={datasetDetail}
                    onGenerate={handleGenerate}
                    generating={generating}
                  />

                  {/* Quality & Gap Section */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <MetadataQualityCard quality={datasetDetail.quality} />
                    <MetadataGapList gaps={datasetDetail.quality.gaps} />
                  </div>

                  {/* Generated Artifacts & Reasoning View */}
                  {generationResult && (
                    <div className="space-y-6 animate-fadeIn">
                      {/* Reasoning Plan */}
                      <ReasoningPanel plan={generationResult.reasoning_plan} />

                      {/* Generated dbt Files Tab View */}
                      <ArtifactViewer
                        sql={generationResult.sql}
                        schemaYml={generationResult.schema_yml}
                        readme={generationResult.readme}
                      />

                      {/* AST & Contract Validation */}
                      <ValidationReportComponent
                        report={generationResult.validation}
                        repairAttempts={generationResult.repair_attempts}
                      />

                      {/* Lineage Diagram */}
                      <LineageGraph
                        sourceName={datasetDetail.name}
                        modelName={generationResult.model_name}
                        published={isPublished}
                      />

                      {/* Governance Gate & DataHub Publish */}
                      <PublishPanel
                        generation={generationResult}
                        onPublished={() => setIsPublished(true)}
                      />
                    </div>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center justify-center p-16 text-center text-slate-500">
                  <Database className="h-12 w-12 text-yellow-400 mb-3" />
                  <p className="font-mono text-xs text-slate-400">Select a dataset from the sidebar to inspect metadata.</p>
                </div>
              )}
            </main>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
