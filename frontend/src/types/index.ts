export interface Gap {
  type: string;
  asset: string;
  severity: 'informational' | 'warning' | 'blocking';
  reason: string;
  generation_impact: string;
}

export interface DimensionScore {
  name: string;
  score: number;
}

export interface QualityReport {
  dataset_name: string;
  overall_score: number;
  dimensions: DimensionScore[];
  gaps: Gap[];
  blocking_count: number;
  warning_count: number;
  informational_count: number;
}

export interface DatasetSummary {
  id: string;
  name: string;
  platform: string;
  environment: string;
  description: string | null;
}

export interface DatasetDetail extends DatasetSummary {
  urn: string;
  owners: string[];
  domains: string[];
  glossary_terms: string[];
  tags: string[];
  column_count: number;
  upstream_count: number;
  downstream_count: number;
  quality: QualityReport;
}

export interface ProvenanceItem {
  decision: string;
  expression: string | null;
  evidence: { asset: string; metadata: string }[];
  confidence: number;
}

export interface ValidationCheck {
  name: string;
  passed: boolean;
  message?: string | null;
}

export interface ValidationReport {
  passed: boolean;
  checks: ValidationCheck[];
  errors: string[];
  warnings: string[];
}

export interface ReasoningTransform {
  name: string;
  expression: string;
  reason: string;
  confidence: number;
}

export interface ReasoningPlan {
  model_name: string;
  grain: string;
  source_tables: string[];
  transformations: ReasoningTransform[];
  tests: string[];
  assumptions: any[];
  metadata_gaps: string[];
}

export interface GenerationResult {
  run_id: string;
  dataset_id: string;
  status: 'DRAFT' | 'VALIDATED' | 'REQUIRES_REVIEW' | 'APPROVED' | 'PUBLISHED' | 'FAILED';
  model_name: string;
  sql: string;
  schema_yml: string;
  readme: string;
  provenance: ProvenanceItem[];
  validation: ValidationReport;
  reasoning_plan: ReasoningPlan;
  repair_attempts: number;
  llm_provider: string;
  blocking_gaps: string[];
}
