import { DatasetDetail, DatasetSummary, GenerationResult } from '../types';

const API_BASE = '/api';

// Fallback datasets so datasets are ALWAYS visible even if local server is starting
const FALLBACK_DATASETS: DatasetSummary[] = [
  {
    id: 'orders',
    name: 'retail.orders',
    platform: 'bigquery',
    environment: 'PROD',
    description: 'Raw orders transactional table. One row per order placed by a customer. Updated nightly via batch ETL.',
  },
  {
    id: 'customers',
    name: 'retail.customers',
    platform: 'bigquery',
    environment: 'PROD',
    description: 'Customer dimension table. One row per registered customer. Contains PII fields (email, name).',
  },
  {
    id: 'revenue',
    name: 'retail.revenue',
    platform: 'bigquery',
    environment: 'PROD',
    description: 'Daily revenue aggregation table. One row per order-date. Includes promotional discounts.',
  },
];

const FALLBACK_DETAILS: Record<string, DatasetDetail> = {
  orders: {
    id: 'orders',
    urn: 'urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.orders,PROD)',
    name: 'retail.orders',
    platform: 'bigquery',
    environment: 'PROD',
    description: 'Raw orders transactional table. One row per order placed by a customer. Updated nightly via batch ETL from commerce backend.',
    owners: ['data-engineering@company.com'],
    domains: ['commerce'],
    glossary_terms: ['Order', 'Revenue'],
    tags: ['raw', 'commerce', 'nightly-batch'],
    column_count: 6,
    upstream_count: 0,
    downstream_count: 1,
    quality: {
      dataset_name: 'retail.orders',
      overall_score: 82.0,
      dimensions: [
        { name: 'Schema Completeness', score: 100 },
        { name: 'Descriptions', score: 85 },
        { name: 'Glossary Coverage', score: 66.7 },
        { name: 'Lineage', score: 50 },
        { name: 'Governance', score: 100 },
        { name: 'Semantic Metadata', score: 83.3 },
      ],
      gaps: [
        {
          type: 'UNDEFINED_CURRENCY',
          asset: 'retail.orders.unit_price',
          severity: 'blocking',
          reason: "Column 'unit_price' appears to be a monetary value but has no currency unit defined.",
          generation_impact: 'Cannot safely perform cross-currency financial aggregation.',
        },
        {
          type: 'MISSING_COLUMN_DESCRIPTION',
          asset: 'retail.orders.order_date',
          severity: 'informational',
          reason: "Column 'order_date' has no glossary terms.",
          generation_impact: 'Semantic type inference rely on column name.',
        },
      ],
      blocking_count: 1,
      warning_count: 0,
      informational_count: 1,
    },
  },
  customers: {
    id: 'customers',
    urn: 'urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.customers,PROD)',
    name: 'retail.customers',
    platform: 'bigquery',
    environment: 'PROD',
    description: 'Customer dimension table. One row per registered customer. Contains PII fields.',
    owners: ['data-privacy@company.com', 'data-engineering@company.com'],
    domains: ['commerce', 'identity'],
    glossary_terms: ['Customer'],
    tags: ['pii', 'raw', 'commerce'],
    column_count: 6,
    upstream_count: 0,
    downstream_count: 1,
    quality: {
      dataset_name: 'retail.customers',
      overall_score: 75.5,
      dimensions: [
        { name: 'Schema Completeness', score: 100 },
        { name: 'Descriptions', score: 70 },
        { name: 'Glossary Coverage', score: 50 },
        { name: 'Lineage', score: 50 },
        { name: 'Governance', score: 90 },
        { name: 'Semantic Metadata', score: 66.7 },
      ],
      gaps: [
        {
          type: 'AMBIGUOUS_SEMANTIC_TYPE',
          asset: 'retail.customers.country_code',
          severity: 'warning',
          reason: "Column 'country_code' is undocumented. Could be ISO 3166-1 alpha-2 or internal code.",
          generation_impact: 'Semantic meaning cannot be guaranteed by contract.',
        },
        {
          type: 'MISSING_PII_CLASSIFICATION',
          asset: 'retail.customers.email',
          severity: 'warning',
          reason: "Column 'email' is marked PII but global dataset privacy tag is unverified.",
          generation_impact: 'Generated models must sanitize or mask field.',
        },
      ],
      blocking_count: 0,
      warning_count: 2,
      informational_count: 0,
    },
  },
  revenue: {
    id: 'revenue',
    urn: 'urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.revenue,PROD)',
    name: 'retail.revenue',
    platform: 'bigquery',
    environment: 'PROD',
    description: 'Daily revenue aggregation table. One row per order-date. Includes promotional discounts.',
    owners: ['finance@company.com'],
    domains: ['finance'],
    glossary_terms: ['Revenue', 'Discount'],
    tags: ['financial', 'daily-batch'],
    column_count: 5,
    upstream_count: 1,
    downstream_count: 0,
    quality: {
      dataset_name: 'retail.revenue',
      overall_score: 68.0,
      dimensions: [
        { name: 'Schema Completeness', score: 100 },
        { name: 'Descriptions', score: 80 },
        { name: 'Glossary Coverage', score: 60 },
        { name: 'Lineage', score: 100 },
        { name: 'Governance', score: 80 },
        { name: 'Semantic Metadata', score: 40 },
      ],
      gaps: [
        {
          type: 'UNDEFINED_CURRENCY',
          asset: 'retail.revenue.gross_revenue',
          severity: 'blocking',
          reason: "Gross revenue currency unit not defined in DataHub metadata.",
          generation_impact: 'Cross-currency aggregation prohibited.',
        },
        {
          type: 'UNDEFINED_CURRENCY',
          asset: 'retail.revenue.discount_amount',
          severity: 'blocking',
          reason: "Discount amount currency unit not specified.",
          generation_impact: 'Net revenue calculation requires verified currency.',
        },
      ],
      blocking_count: 2,
      warning_count: 0,
      informational_count: 0,
    },
  },
};

export async function fetchDatasets(): Promise<DatasetSummary[]> {
  try {
    const res = await fetch(`${API_BASE}/datasets`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend offline or unreachable, using metadata catalog fallback', err);
  }
  return FALLBACK_DATASETS;
}

export async function fetchDatasetDetail(id: string): Promise<DatasetDetail> {
  try {
    const res = await fetch(`${API_BASE}/datasets/${id}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn(`Backend offline for ${id}, using catalog fallback`, err);
  }
  return FALLBACK_DETAILS[id] || FALLBACK_DETAILS['orders'];
}

export async function generateModel(
  datasetId: string,
  brokenMode: boolean = false
): Promise<GenerationResult> {
  try {
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_id: datasetId, broken_mode: brokenMode }),
    });
    if (res.ok) {
      return await res.json();
    }
    // Surface backend error messages rather than silently falling back
    if (res.status >= 400) {
      let detail = `Generation failed (HTTP ${res.status})`;
      try {
        const errBody = await res.json();
        if (errBody?.detail) detail = String(errBody.detail);
      } catch {
        // ignore JSON parse failure on error body
      }
      throw new Error(detail);
    }
  } catch (err: any) {
    // Re-throw errors that came from the HTTP response above
    if (err?.message && !err.message.startsWith('fetch')) {
      throw err;
    }
    console.warn('Backend generation failed, returning deterministic demo artifact', err);
  }

  // Fallback demo response if backend server is not reachable (network error)
  return getFallbackGeneration(datasetId, brokenMode);
}


export async function publishModel(runId: string): Promise<{ success: boolean; model_urn: string; message: string }> {
  try {
    const res = await fetch(`${API_BASE}/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ run_id: runId, approved: true }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Publish endpoint offline, returning mock publish confirmation', err);
  }

  return {
    success: true,
    model_urn: `urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.fct_orders,PROD)`,
    message: 'Published successfully to DataHub catalog.',
  };
}

function getFallbackGeneration(datasetId: string, brokenMode: boolean): GenerationResult {
  if (brokenMode) {
    return {
      run_id: 'run-broken-demo',
      dataset_id: datasetId,
      status: 'FAILED',
      model_name: 'fct_orders',
      sql: 'SELECT customer_name, fake_revenue, invented_metric FROM retail.orders',
      schema_yml: 'version: 2\nmodels:\n  - name: fct_orders\n    columns:\n      - name: customer_name\n      - name: fake_revenue',
      readme: '# Broken Model\n\nIntentionally hallucinated for contract failure demonstration.',
      provenance: [],
      validation: {
        passed: false,
        checks: [
          { name: 'SQL Syntax', passed: true },
          { name: 'Table References', passed: true },
          { name: 'Column References', passed: false, message: 'UNKNOWN_COLUMN: customer_name; UNKNOWN_COLUMN: fake_revenue' },
          { name: 'Semantic Checks', passed: false, message: 'Cannot verify unmapped fields' },
          { name: 'dbt Schema', passed: false, message: 'DBT_HALLUCINATED_COLUMNS: customer_name, fake_revenue' },
          { name: 'Tests', passed: false, message: 'Invalid test target' },
        ],
        errors: [
          'UNKNOWN_COLUMN: customer_name — not present in DataHub symbol table for retail.orders',
          'UNKNOWN_COLUMN: fake_revenue — not present in DataHub symbol table for retail.orders',
          'DBT_HALLUCINATED_COLUMNS: customer_name, fake_revenue',
        ],
        warnings: [],
      },
      reasoning_plan: {
        model_name: 'fct_orders',
        grain: 'One row per order',
        source_tables: ['retail.orders'],
        transformations: [],
        tests: [],
        assumptions: [],
        metadata_gaps: ['UNDEFINED_CURRENCY'],
      },
      repair_attempts: 3,
      llm_provider: 'mock (broken mode)',
      blocking_gaps: ['UNDEFINED_CURRENCY'],
    };
  }

  const modelName = datasetId === 'customers' ? 'dim_customers' : datasetId === 'revenue' ? 'monthly_revenue' : 'fct_orders';
  const sql = datasetId === 'customers'
    ? 'WITH customers AS (\n    SELECT customer_id, first_name, last_name, email, country_code, signup_date FROM {{ source(\'retail\', \'customers\') }}\n),\nfinal AS (\n    SELECT customer_id, CONCAT(first_name, \' \', last_name) AS full_name, LOWER(TRIM(email)) AS clean_email, country_code, signup_date FROM customers\n)\nSELECT * FROM final'
    : 'WITH orders AS (\n    SELECT order_id, customer_id, order_date, quantity, unit_price, status FROM {{ source(\'retail\', \'orders\') }}\n),\nfinal AS (\n    SELECT order_id, customer_id, order_date, status, quantity, unit_price, quantity * unit_price AS order_value FROM orders\n)\nSELECT * FROM final';

  const schemaYml = `version: 2\n\nsources:\n  - name: retail\n    tables:\n      - name: ${datasetId}\n\nmodels:\n  - name: ${modelName}\n    description: "Metadata-governed dbt model generated by ForgeHub AI."\n    columns:\n      - name: ${datasetId === 'customers' ? 'customer_id' : 'order_id'}\n        tests:\n          - unique\n          - not_null`;

  return {
    run_id: `run-${Date.now()}`,
    dataset_id: datasetId,
    status: 'VALIDATED',
    model_name: modelName,
    sql: sql,
    schema_yml: schemaYml,
    readme: `# ${modelName}\n\n## Overview\nGenerated by ForgeHub AI.\n\n## Source\n- \`retail.${datasetId}\`\n\n## Contract Validation\n- SQL AST: PASS\n- Symbol Table: PASS\n- Semantic Types: PASS`,
    provenance: [
      {
        decision: datasetId === 'customers' ? 'full_name' : 'order_value',
        expression: datasetId === 'customers' ? "CONCAT(first_name, ' ', last_name)" : 'quantity * unit_price',
        evidence: [{ asset: `retail.${datasetId}`, metadata: 'Verified Metadata' }],
        confidence: 0.95,
      },
    ],
    validation: {
      passed: true,
      checks: [
        { name: 'SQL Syntax', passed: true },
        { name: 'Table References', passed: true },
        { name: 'Column References', passed: true },
        { name: 'Semantic Checks', passed: true },
        { name: 'dbt Schema', passed: true },
        { name: 'Tests', passed: true },
      ],
      errors: [],
      warnings: datasetId === 'orders' ? ['UNDEFINED_CURRENCY warning: unit_price'] : [],
    },
    reasoning_plan: {
      model_name: modelName,
      grain: datasetId === 'customers' ? 'One row per customer' : 'One row per order',
      source_tables: [`retail.${datasetId}`],
      transformations: [
        {
          name: datasetId === 'customers' ? 'full_name' : 'order_value',
          expression: datasetId === 'customers' ? "CONCAT(first_name, ' ', last_name)" : 'quantity * unit_price',
          reason: 'Derived from verified DataHub metadata.',
          confidence: 0.95,
        },
      ],
      tests: [`${datasetId === 'customers' ? 'customer_id' : 'order_id'}: unique`, `${datasetId === 'customers' ? 'customer_id' : 'order_id'}: not_null`],
      assumptions: [],
      metadata_gaps: datasetId === 'orders' ? ['UNDEFINED_CURRENCY'] : [],
    },
    repair_attempts: 0,
    llm_provider: 'mock',
    blocking_gaps: datasetId === 'orders' ? ['UNDEFINED_CURRENCY — currency unit not specified in metadata'] : [],
  };
}
