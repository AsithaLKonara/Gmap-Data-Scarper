/**
 * Enhanced Query Optimizer - Expands and optimizes search queries
 * Uses rule-based logic with context awareness, scoring, and learning
 */

export interface QueryContext {
  location?: string;
  fieldOfStudy?: string;
  studentOnly?: boolean;
  institution?: string;
  educationLevel?: string[];
}

export interface OptimizedQuery {
  query: string;
  priority: number; // 1-10, higher = more important
  source: 'original' | 'location' | 'field' | 'synonym' | 'education' | 'local_context' | 'platform' | 'intent';
}

export interface QueryScore {
  query: string;
  score: number;
  factors: {
    length: number;
    specificity: number;
    clarity: number;
    platformFit: number;
    uniqueness: number;
  };
}

export interface QueryIntent {
  type: 'student_search' | 'business_search' | 'job_search' | 'location_search' | 'mixed';
  confidence: number;
  entities: {
    location?: string;
    field?: string;
    educationLevel?: string;
    entityType?: 'individual' | 'business';
  };
}

export interface QueryValidation {
  isValid: boolean;
  issues: string[];
  suggestions: string[];
  estimatedResults: 'high' | 'medium' | 'low';
}

export interface QueryAnalytics {
  query: string;
  resultsCount: number;
  platforms: string[];
  timestamp: Date;
  successRate: number;
}

/**
 * Field of study synonyms and variations
 */
const FIELD_SYNONYMS: Record<string, string[]> = {
  'ICT': ['Information Technology', 'IT', 'Computer Science', 'CS', 'Computing'],
  'Information Technology': ['ICT', 'IT', 'Computer Science', 'CS'],
  'Computer Science': ['CS', 'ICT', 'IT', 'Information Technology', 'Computing'],
  'Engineering': ['Eng', 'Engineering Science'],
  'Business': ['Business Administration', 'Commerce', 'Management'],
  'Medicine': ['Medical', 'MBBS', 'Health Sciences'],
  'Law': ['Legal Studies', 'Jurisprudence'],
};

/**
 * Location-specific context (universities, landmarks, etc.)
 */
const LOCATION_CONTEXT: Record<string, string[]> = {
  'kandy': ['University of Peradeniya', 'UOP', 'Peradeniya University'],
  'colombo': ['University of Colombo', 'UOC', 'Colombo University'],
  'moratuwa': ['University of Moratuwa', 'UOM', 'Moratuwa University'],
  'jaffna': ['University of Jaffna', 'UOJ', 'Jaffna University'],
  'sri lanka': ['Sri Lankan', 'SL'],
};

/**
 * Extract location from query if not provided in context
 */
export function extractLocationFromQuery(query: string): string | null {
  const locationPatterns = [
    /in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/g,
    /near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/g,
    /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:sri\s+lanka|sl)\b/gi,
  ];
  
  for (const pattern of locationPatterns) {
    const match = query.match(pattern);
    if (match) {
      return match[1] || match[0].replace(/^(in|near)\s+/i, '');
    }
  }
  
  // Check common locations
  const commonLocations = ['kandy', 'colombo', 'galle', 'jaffna', 'negombo', 'matale', 'anuradhapura'];
  const queryLower = query.toLowerCase();
  for (const loc of commonLocations) {
    if (queryLower.includes(loc)) {
      return loc;
    }
  }
  
  return null;
}

/**
 * Extract field of study from query
 */
export function extractFieldFromQuery(query: string): string | null {
  const queryLower = query.toLowerCase();
  
  for (const [field, synonyms] of Object.entries(FIELD_SYNONYMS)) {
    if (queryLower.includes(field.toLowerCase())) {
      return field;
    }
    for (const synonym of synonyms) {
      if (queryLower.includes(synonym.toLowerCase())) {
        return field;
      }
    }
  }
  
  return null;
}

/**
 * Smart context extraction from query
 */
export function extractContextFromQuery(query: string): QueryContext {
  return {
    location: extractLocationFromQuery(query) || undefined,
    fieldOfStudy: extractFieldFromQuery(query) || undefined,
    studentOnly: /student|undergraduate|graduate/i.test(query),
  };
}

/**
 * Score query quality (0-100) based on multiple factors
 */
export function scoreQuery(
  query: string,
  context: QueryContext,
  platforms: string[] = []
): QueryScore {
  const factors = {
    length: scoreLength(query),
    specificity: scoreSpecificity(query, context),
    clarity: scoreClarity(query),
    platformFit: scorePlatformFit(query, platforms),
    uniqueness: 50, // Will be calculated when comparing with other queries
  };
  
  // Weighted average
  const score = Math.round(
    factors.length * 0.15 +
    factors.specificity * 0.30 +
    factors.clarity * 0.25 +
    factors.platformFit * 0.20 +
    factors.uniqueness * 0.10
  );
  
  return { query, score, factors };
}

function scoreLength(query: string): number {
  const len = query.length;
  if (len >= 10 && len <= 50) return 100;
  if (len >= 5 && len <= 70) return 80;
  if (len < 5) return 30;
  return 50;
}

function scoreSpecificity(query: string, context: QueryContext): number {
  let score = 50;
  const queryLower = query.toLowerCase();
  
  if (context.location || /in\s+\w+|near\s+\w+/.test(query)) {
    score += 20;
  }
  
  if (context.fieldOfStudy || /ICT|IT|computer|engineering/i.test(query)) {
    score += 15;
  }
  
  if (context.studentOnly || /student|undergraduate|graduate/i.test(query)) {
    score += 10;
  }
  
  if (/university|college|institute/i.test(query)) {
    score += 5;
  }
  
  return Math.min(100, score);
}

function scoreClarity(query: string): number {
  let score = 70;
  
  const vagueWords = ['related', 'things', 'stuff', 'etc'];
  const vagueCount = vagueWords.filter(word => 
    query.toLowerCase().includes(word)
  ).length;
  score -= vagueCount * 10;
  
  if (/find|search|looking for/i.test(query)) {
    score += 10;
  }
  
  if (query.split(/\s+/).length >= 3) {
    score += 10;
  }
  
  return Math.max(0, Math.min(100, score));
}

function scorePlatformFit(query: string, platforms: string[]): number {
  if (platforms.length === 0) return 50;
  
  let score = 50;
  const queryLower = query.toLowerCase();
  
  if (platforms.includes('google_maps')) {
    if (/in\s+\w+|near\s+\w+|location|address/i.test(query)) {
      score += 20;
    }
  }
  
  if (platforms.some(p => ['facebook', 'linkedin', 'instagram'].includes(p))) {
    if (/student|profile|person|individual/i.test(query)) {
      score += 20;
    }
  }
  
  if (platforms.includes('linkedin')) {
    if (/professional|career|job|company/i.test(query)) {
      score += 15;
    }
  }
  
  return Math.min(100, score);
}

/**
 * Detect query intent and enhance accordingly
 */
export function detectIntent(query: string, context: QueryContext): QueryIntent {
  const queryLower = query.toLowerCase();
  const entities: QueryIntent['entities'] = {};
  
  const locationMatch = query.match(/in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i);
  entities.location = locationMatch?.[1] || context.location;
  
  for (const [field, synonyms] of Object.entries(FIELD_SYNONYMS)) {
    if (queryLower.includes(field.toLowerCase()) || 
        synonyms.some(s => queryLower.includes(s.toLowerCase()))) {
      entities.field = field;
      break;
    }
  }
  entities.field = entities.field || context.fieldOfStudy;
  
  if (/undergraduate|bachelor|degree/i.test(query)) {
    entities.educationLevel = 'undergraduate';
  } else if (/graduate|master|phd|doctorate/i.test(query)) {
    entities.educationLevel = 'graduate';
  }
  
  if (/student|learner|pupil|individual/i.test(query)) {
    entities.entityType = 'individual';
  } else if (/business|company|organization|firm/i.test(query)) {
    entities.entityType = 'business';
  }
  
  let type: QueryIntent['type'] = 'mixed';
  let confidence = 50;
  
  if (/student|undergraduate|graduate|university|college/i.test(query)) {
    type = 'student_search';
    confidence = 80;
  } else if (/business|company|shop|store|restaurant/i.test(query)) {
    type = 'business_search';
    confidence = 80;
  } else if (/job|career|hire|employment/i.test(query)) {
    type = 'job_search';
    confidence = 75;
  } else if (/in\s+\w+|near\s+\w+|location|address/i.test(query)) {
    type = 'location_search';
    confidence = 70;
  }
  
  if (context.studentOnly && type === 'student_search') confidence += 10;
  if (context.location && entities.location) confidence += 10;
  if (context.fieldOfStudy && entities.field) confidence += 10;
  
  return {
    type,
    confidence: Math.min(100, confidence),
    entities
  };
}

/**
 * Enhance queries based on detected intent
 */
export function enhanceByIntent(
  queries: string[],
  intent: QueryIntent
): string[] {
  const enhanced: string[] = [];
  
  for (const query of queries) {
    enhanced.push(query);
    
    switch (intent.type) {
      case 'student_search':
        if (!query.includes('student')) {
          enhanced.push(`${query} student`);
        }
        if (intent.entities.location && !query.includes(intent.entities.location)) {
          enhanced.push(`${query} in ${intent.entities.location}`);
        }
        if (intent.entities.field && !query.includes(intent.entities.field)) {
          enhanced.push(`${intent.entities.field} ${query}`);
        }
        break;
        
      case 'business_search':
        if (!query.includes('business') && !query.includes('company')) {
          enhanced.push(`${query} business`);
        }
        if (intent.entities.location) {
          enhanced.push(`${query} ${intent.entities.location}`);
        }
        break;
        
      case 'location_search':
        enhanced.push(`${query} business`);
        enhanced.push(`${query} services`);
        break;
    }
  }
  
  return Array.from(new Set(enhanced));
}

/**
 * Generate query variations based on context
 */
function generateVariations(
  baseQuery: string,
  context: QueryContext
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  const queryLower = baseQuery.toLowerCase();
  
  if (context.location) {
    variations.push(...generateLocationVariations(baseQuery, context.location));
  }
  
  if (context.fieldOfStudy) {
    variations.push(...generateFieldVariations(baseQuery, context.fieldOfStudy));
  }
  
  if (context.studentOnly || queryLower.includes('student')) {
    variations.push(...generateEducationVariations(baseQuery, context));
  }
  
  if (context.institution) {
    variations.push({
      query: `${baseQuery} ${context.institution}`,
      priority: 8,
      source: 'local_context'
    });
  }
  
  if (context.location) {
    variations.push(...generateLocalContextVariations(baseQuery, context.location));
  }
  
  variations.push(...generateSynonymVariations(baseQuery, context));
  variations.push(...generatePhraseVariations(baseQuery, context));
  
  return variations;
}

function generateLocationVariations(
  query: string,
  location: string
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  const locationLower = location.toLowerCase();
  
  if (!query.toLowerCase().includes(locationLower)) {
    variations.push({
      query: `${query} in ${location}`,
      priority: 9,
      source: 'location'
    });
    
    variations.push({
      query: `${query} ${location}`,
      priority: 8,
      source: 'location'
    });
    
    variations.push({
      query: `${query} near ${location}`,
      priority: 7,
      source: 'location'
    });
    
    variations.push({
      query: `${query} ${location} area`,
      priority: 6,
      source: 'location'
    });
  }
  
  return variations;
}

function generateFieldVariations(
  query: string,
  fieldOfStudy: string
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  const fieldLower = fieldOfStudy.toLowerCase();
  const queryLower = query.toLowerCase();
  
  const synonyms = FIELD_SYNONYMS[fieldOfStudy] || [];
  
  if (!queryLower.includes(fieldLower)) {
    variations.push({
      query: `${fieldOfStudy} ${query}`,
      priority: 9,
      source: 'field'
    });
    
    variations.push({
      query: `${query} ${fieldOfStudy}`,
      priority: 8,
      source: 'field'
    });
  }
  
  for (const synonym of synonyms) {
    if (!queryLower.includes(synonym.toLowerCase())) {
      variations.push({
        query: query.replace(new RegExp(fieldOfStudy, 'gi'), synonym),
        priority: 7,
        source: 'synonym'
      });
    }
  }
  
  return variations;
}

function generateEducationVariations(
  query: string,
  context: QueryContext
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  const queryLower = query.toLowerCase();
  
  if (context.studentOnly || queryLower.includes('undergraduate')) {
    if (!queryLower.includes('undergraduate')) {
      variations.push({
        query: `${query} undergraduate`,
        priority: 8,
        source: 'education'
      });
    }
    
    variations.push({
      query: query.replace(/student/gi, 'undergraduate student'),
      priority: 7,
      source: 'education'
    });
    
    variations.push({
      query: `${query} bachelor degree`,
      priority: 6,
      source: 'education'
    });
  }
  
  if (queryLower.includes('student')) {
    variations.push({
      query: `${query} university`,
      priority: 7,
      source: 'education'
    });
    
    variations.push({
      query: `${query} college`,
      priority: 6,
      source: 'education'
    });
  }
  
  return variations;
}

function generateLocalContextVariations(
  query: string,
  location: string
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  const locationLower = location.toLowerCase();
  
  const contexts = LOCATION_CONTEXT[locationLower] || [];
  
  for (const contextItem of contexts) {
    variations.push({
      query: `${query} ${contextItem}`,
      priority: 6,
      source: 'local_context'
    });
  }
  
  return variations;
}

function generateSynonymVariations(
  query: string,
  context: QueryContext
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  const queryLower = query.toLowerCase();
  
  const synonymMap: Record<string, string[]> = {
    'related': ['in', 'about', 'for'],
    'students': ['learners', 'undergraduates', 'graduates'],
    'undergraduates': ['students', 'bachelor students'],
  };
  
  for (const [word, synonyms] of Object.entries(synonymMap)) {
    if (queryLower.includes(word)) {
      for (const synonym of synonyms) {
        const newQuery = query.replace(new RegExp(word, 'gi'), synonym);
        if (newQuery !== query) {
          variations.push({
            query: newQuery,
            priority: 5,
            source: 'synonym'
          });
        }
      }
    }
  }
  
  return variations;
}

function generatePhraseVariations(
  query: string,
  context: QueryContext
): OptimizedQuery[] {
  const variations: OptimizedQuery[] = [];
  
  const words = query.split(/\s+/);
  
  if (context.location && words.length > 3) {
    const withoutLocation = words.filter(w => 
      !w.toLowerCase().includes(context.location!.toLowerCase())
    );
    if (withoutLocation.length < words.length) {
      variations.push({
        query: `${withoutLocation.join(' ')} ${context.location}`,
        priority: 5,
        source: 'synonym'
      });
    }
  }
  
  if (query.toLowerCase().includes('student')) {
    variations.push({
      query: `looking for ${query}`,
      priority: 4,
      source: 'synonym'
    });
  }
  
  return variations;
}

/**
 * Platform-specific query optimization
 */
export function optimizeForPlatforms(
  baseQueries: string[],
  platforms: string[],
  context: QueryContext
): string[] {
  const allQueries: string[] = [];
  
  for (const baseQuery of baseQueries) {
    for (const platform of platforms) {
      switch (platform) {
        case 'google_maps':
          allQueries.push(baseQuery);
          if (context.location) {
            allQueries.push(`${baseQuery} ${context.location}`);
            allQueries.push(`${context.location} ${baseQuery}`);
          }
          if (baseQuery.includes('student')) {
            allQueries.push(baseQuery.replace(/student/gi, 'student services'));
          }
          break;
          
        case 'facebook':
          allQueries.push(baseQuery);
          allQueries.push(`${baseQuery} page`);
          allQueries.push(`${baseQuery} group`);
          break;
          
        case 'linkedin':
          allQueries.push(baseQuery);
          allQueries.push(`${baseQuery} professional`);
          if (context.fieldOfStudy) {
            allQueries.push(`${context.fieldOfStudy} professionals ${context.location || ''}`);
          }
          break;
          
        case 'instagram':
          allQueries.push(baseQuery);
          allQueries.push(`#${baseQuery.replace(/\s+/g, '')}`);
          break;
          
        default:
          allQueries.push(baseQuery);
      }
    }
  }
  
  return Array.from(new Set(allQueries));
}

/**
 * Smart query deduplication
 */
function smartDeduplicate(queries: OptimizedQuery[]): OptimizedQuery[] {
  const merged: OptimizedQuery[] = [];
  const seen = new Set<string>();
  
  for (const query of queries) {
    const normalized = normalizeQuery(query.query);
    
    if (seen.has(normalized)) {
      continue;
    }
    
    const similar = merged.find(q => 
      areQueriesSimilar(normalizeQuery(q.query), normalized)
    );
    
    if (similar) {
      if (query.priority > similar.priority) {
        const index = merged.indexOf(similar);
        merged[index] = query;
      }
    } else {
      merged.push(query);
      seen.add(normalized);
    }
  }
  
  return merged;
}

function normalizeQuery(query: string): string {
  return query
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s]/g, '');
}

function areQueriesSimilar(query1: string, query2: string): boolean {
  const words1 = new Set(query1.split(/\s+/));
  const words2 = new Set(query2.split(/\s+/));
  
  const intersection = new Set([...words1].filter(w => words2.has(w)));
  const union = new Set([...words1, ...words2]);
  
  const similarity = intersection.size / union.size;
  return similarity >= 0.8;
}

/**
 * Calculate uniqueness score
 */
function calculateUniqueness(
  query: string,
  allQueries: Array<{ query: string }>,
  currentIndex: number
): number {
  const queryWords = new Set(query.toLowerCase().split(/\s+/));
  let similaritySum = 0;
  let count = 0;
  
  for (let i = 0; i < allQueries.length; i++) {
    if (i === currentIndex) continue;
    
    const otherWords = new Set(allQueries[i].query.toLowerCase().split(/\s+/));
    const intersection = new Set([...queryWords].filter(w => otherWords.has(w)));
    const union = new Set([...queryWords, ...otherWords]);
    const similarity = intersection.size / union.size;
    
    similaritySum += similarity;
    count++;
  }
  
  const avgSimilarity = count > 0 ? similaritySum / count : 0;
  return Math.round((1 - avgSimilarity) * 100);
}

/**
 * Score and prioritize all queries
 */
function prioritizeQueries(
  queries: OptimizedQuery[],
  context: QueryContext,
  platforms: string[]
): OptimizedQuery[] {
  const scored = queries.map(q => ({
    ...q,
    qualityScore: scoreQuery(q.query, context, platforms).score
  }));
  
  const withUniqueness = scored.map((q, idx) => {
    const uniqueness = calculateUniqueness(q.query, scored, idx);
    return {
      ...q,
      qualityScore: q.qualityScore * 0.9 + uniqueness * 0.1
    };
  });
  
  return withUniqueness
    .map(q => ({
      ...q,
      combinedScore: q.qualityScore * 0.6 + q.priority * 0.4
    }))
    .sort((a, b) => b.combinedScore - a.combinedScore)
    .map(({ qualityScore, combinedScore, ...rest }) => rest);
}

/**
 * Query Learning System
 */
class QueryLearningSystem {
  private analytics: QueryAnalytics[] = [];
  private readonly STORAGE_KEY = 'query_analytics';
  
  constructor() {
    this.loadAnalytics();
  }
  
  recordQuery(
    query: string,
    resultsCount: number,
    platforms: string[]
  ): void {
    const analytics: QueryAnalytics = {
      query: query.toLowerCase().trim(),
      resultsCount,
      platforms,
      timestamp: new Date(),
      successRate: resultsCount > 0 ? 100 : 0
    };
    
    this.analytics.push(analytics);
    this.saveAnalytics();
  }
  
  getSuccessfulPatterns(): {
    keywords: string[];
    structures: string[];
    avgResults: number;
  } {
    const successful = this.analytics.filter(a => a.resultsCount > 5);
    
    if (successful.length === 0) {
      return { keywords: [], structures: [], avgResults: 0 };
    }
    
    const keywordCounts = new Map<string, number>();
    successful.forEach(a => {
      const words = a.query.split(/\s+/);
      words.forEach(word => {
        if (word.length > 3) {
          keywordCounts.set(word, (keywordCounts.get(word) || 0) + a.resultsCount);
        }
      });
    });
    
    const topKeywords = Array.from(keywordCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([word]) => word);
    
    const structures: string[] = [];
    successful.forEach(a => {
      if (/in\s+\w+/.test(a.query)) structures.push('location-based');
      if (/student/.test(a.query)) structures.push('student-focused');
      if (/university|college/.test(a.query)) structures.push('education-focused');
    });
    
    const uniqueStructures = [...new Set(structures)];
    const avgResults = successful.reduce((sum, a) => sum + a.resultsCount, 0) / successful.length;
    
    return {
      keywords: topKeywords,
      structures: uniqueStructures,
      avgResults: Math.round(avgResults)
    };
  }
  
  boostSimilarQueries(queries: OptimizedQuery[]): OptimizedQuery[] {
    const patterns = this.getSuccessfulPatterns();
    
    return queries.map(q => {
      let boost = 0;
      const queryLower = q.query.toLowerCase();
      
      patterns.keywords.forEach(keyword => {
        if (queryLower.includes(keyword)) {
          boost += 2;
        }
      });
      
      patterns.structures.forEach(structure => {
        if (structure === 'location-based' && /in\s+\w+/.test(queryLower)) {
          boost += 3;
        }
        if (structure === 'student-focused' && /student/.test(queryLower)) {
          boost += 3;
        }
      });
      
      return {
        ...q,
        priority: Math.min(10, q.priority + boost)
      };
    });
  }
  
  private loadAnalytics(): void {
    if (typeof window === 'undefined') return;
    
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        this.analytics = data.map((a: any) => ({
          ...a,
          timestamp: new Date(a.timestamp)
        }));
      }
    } catch (e) {
      console.error('Failed to load query analytics:', e);
    }
  }
  
  private saveAnalytics(): void {
    if (typeof window === 'undefined') return;
    
    try {
      const toSave = this.analytics.slice(-1000);
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(toSave));
    } catch (e) {
      console.error('Failed to save query analytics:', e);
    }
  }
}

export const queryLearning = new QueryLearningSystem();

/**
 * Main query optimizer function
 */
export function optimizeQueries(
  baseQueries: string[],
  context: QueryContext = {}
): OptimizedQuery[] {
  const optimized: OptimizedQuery[] = [];
  
  for (const baseQuery of baseQueries) {
    if (!baseQuery.trim()) continue;
    
    optimized.push({
      query: baseQuery.trim(),
      priority: 10,
      source: 'original'
    });
    
    const variations = generateVariations(baseQuery, context);
    optimized.push(...variations);
  }
  
  return deduplicateAndSort(optimized);
}

function deduplicateAndSort(queries: OptimizedQuery[]): OptimizedQuery[] {
  const seen = new Set<string>();
  const unique: OptimizedQuery[] = [];
  
  for (const q of queries) {
    const normalized = q.query.toLowerCase().trim();
    if (!seen.has(normalized) && normalized.length > 0) {
      seen.add(normalized);
      unique.push(q);
    }
  }
  
  const sourceOrder = ['original', 'location', 'field', 'education', 'local_context', 'platform', 'intent', 'synonym'];
  return unique.sort((a, b) => {
    if (b.priority !== a.priority) {
      return b.priority - a.priority;
    }
    return sourceOrder.indexOf(a.source) - sourceOrder.indexOf(b.source);
  });
}

/**
 * Get top N optimized queries
 */
export function getTopQueries(
  optimized: OptimizedQuery[],
  limit: number = 10
): string[] {
  return optimized
    .slice(0, limit)
    .map(q => q.query);
}

/**
 * Enhanced main optimizer with all features
 */
export function optimizeQueriesAdvanced(
  baseQueries: string[],
  context: QueryContext,
  platforms: string[] = [],
  options: {
    enableLearning?: boolean;
    enablePlatformOptimization?: boolean;
    maxQueries?: number;
    minQualityScore?: number;
  } = {}
): {
  queries: OptimizedQuery[];
  intent: QueryIntent;
  analytics: {
    totalGenerated: number;
    afterDeduplication: number;
    afterScoring: number;
    avgQualityScore: number;
  };
} {
  const {
    enableLearning = true,
    enablePlatformOptimization = true,
    maxQueries = 20,
    minQualityScore = 40
  } = options;
  
  let optimized = optimizeQueries(baseQueries, context);
  
  const intent = detectIntent(baseQueries[0] || '', context);
  
  const enhancedQueries = enhanceByIntent(
    optimized.map(q => q.query),
    intent
  );
  optimized = optimizeQueries(enhancedQueries, context);
  
  if (enablePlatformOptimization && platforms.length > 0) {
    const platformQueries = optimizeForPlatforms(
      optimized.map(q => q.query),
      platforms,
      context
    );
    optimized = optimizeQueries(platformQueries, context);
  }
  
  optimized = smartDeduplicate(optimized);
  optimized = prioritizeQueries(optimized, context, platforms);
  
  if (enableLearning) {
    optimized = queryLearning.boostSimilarQueries(optimized);
    optimized.sort((a, b) => b.priority - a.priority);
  }
  
  optimized = optimized.filter(q => {
    const score = scoreQuery(q.query, context, platforms);
    return score.score >= minQualityScore;
  });
  
  optimized = optimized.slice(0, maxQueries);
  
  const avgQualityScore = optimized.length > 0
    ? optimized.reduce((sum, q) => {
        const score = scoreQuery(q.query, context, platforms);
        return sum + score.score;
      }, 0) / optimized.length
    : 0;
  
  return {
    queries: optimized,
    intent,
    analytics: {
      totalGenerated: enhancedQueries.length,
      afterDeduplication: optimized.length,
      afterScoring: optimized.length,
      avgQualityScore: Math.round(avgQualityScore)
    }
  };
}

/**
 * Validate query and provide suggestions
 */
export function validateQuery(
  query: string,
  context: QueryContext
): QueryValidation {
  const issues: string[] = [];
  const suggestions: string[] = [];
  
  if (query.length < 5) {
    issues.push('Query is too short (minimum 5 characters)');
    suggestions.push('Add more context to your query');
  }
  
  if (query.length > 100) {
    issues.push('Query is too long (maximum 100 characters)');
    suggestions.push('Simplify your query');
  }
  
  if (!context.location && !/in\s+\w+|near\s+\w+/.test(query)) {
    issues.push('No location specified');
    suggestions.push('Add a location (e.g., "in kandy", "near colombo")');
  }
  
  const vagueWords = ['related', 'things', 'stuff'];
  const hasVague = vagueWords.some(word => query.toLowerCase().includes(word));
  if (hasVague) {
    issues.push('Query contains vague terms');
    suggestions.push('Use more specific keywords');
  }
  
  let estimatedResults: 'high' | 'medium' | 'low' = 'medium';
  const score = scoreQuery(query, context, []).score;
  if (score >= 70) estimatedResults = 'high';
  else if (score < 50) estimatedResults = 'low';
  
  return {
    isValid: issues.length === 0,
    issues,
    suggestions,
    estimatedResults
  };
}

