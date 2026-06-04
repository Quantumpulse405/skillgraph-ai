'use client';

import { useState } from 'react';

type AnalysisResult = {
  skills: string[];
  missing_skills: string[];
  readiness_score: number;
  roadmap: string[];
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file || !jobDescription) {
      setError('Please provide both a resume (PDF) and a job description.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jobDescription);

    try {
      // In development, assume the FastAPI backend runs on localhost:8000
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Analysis failed. Please try again.');
      }

      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl">
            Resume Analyzer
          </h1>
          <p className="mt-4 text-lg text-gray-500">
            Upload your resume and a job description to see how well you match and get a learning roadmap.
          </p>
        </div>

        <div className="bg-white shadow sm:rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <div className="space-y-6">
              <div>
                <label htmlFor="resume" className="block text-sm font-medium text-gray-700">
                  Upload Resume (PDF)
                </label>
                <div className="mt-1">
                  <input
                    type="file"
                    id="resume"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-gray-300 rounded-md shadow-sm p-2"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="job-description" className="block text-sm font-medium text-gray-700">
                  Job Description
                </label>
                <div className="mt-1">
                  <textarea
                    id="job-description"
                    rows={6}
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-3 border"
                    placeholder="Paste the job description here..."
                  />
                </div>
              </div>

              {error && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">{error}</h3>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={handleAnalyze}
                disabled={loading || !file || !jobDescription}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </div>
        </div>

        {result && (
          <div className="bg-white shadow sm:rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 bg-blue-50 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Analysis Results</h3>
              <div className="flex items-center">
                <span className="text-sm text-gray-500 mr-2">Readiness Score:</span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  result.readiness_score >= 80 ? 'bg-green-100 text-green-800' :
                  result.readiness_score >= 50 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {result.readiness_score}%
                </span>
              </div>
            </div>
            <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
              <dl className="sm:divide-y sm:divide-gray-200">
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Skills Found</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    <div className="flex flex-wrap gap-2">
                      {result.skills.length > 0 ? result.skills.map((skill, index) => (
                        <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-green-100 text-green-800">
                          {skill}
                        </span>
                      )) : "None identified"}
                    </div>
                  </dd>
                </div>
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Missing Skills</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    <div className="flex flex-wrap gap-2">
                      {result.missing_skills.length > 0 ? result.missing_skills.map((skill, index) => (
                        <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-red-100 text-red-800">
                          {skill}
                        </span>
                      )) : "None identified"}
                    </div>
                  </dd>
                </div>
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Learning Roadmap</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                      {result.roadmap.length > 0 ? result.roadmap.map((step, index) => (
                        <li key={index} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                          <div className="w-0 flex-1 flex items-center">
                            <span className="flex-shrink-0 h-5 w-5 text-blue-500 flex items-center justify-center font-bold">{index + 1}.</span>
                            <span className="ml-2 flex-1 w-0">{step}</span>
                          </div>
                        </li>
                      )) : <li className="pl-3 pr-4 py-3 text-sm text-gray-500">No steps suggested</li>}
                    </ul>
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
