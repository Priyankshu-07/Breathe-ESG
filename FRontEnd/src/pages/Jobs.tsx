import React, { useState, useEffect } from 'react';
import {
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Check,
  Clock,
  Loader,
} from 'lucide-react';

import Layout from '../components/Layout';
import StatusBadge from '../components/StatusBadge';
import { apiFetch } from '../api/client';

interface IngestionRow {
  id: string;
  row_index: number;
  status: string;
  error_message: string;
  raw_data: Record<string, any>;
}

interface Job {
  id: string;
  raw_filename: string;
  source_type: string;
  status: string;
  row_count: number;
  error_count: number;
  uploaded_by_email: string;
  created_at: string;
  completed_at: string | null;
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);

  const [jobRows, setJobRows] = useState<
    Record<string, IngestionRow[]>
  >({});

  const [isLoading, setIsLoading] = useState(true);

  const [loadingRows, setLoadingRows] = useState<string | null>(
    null
  );

  const [error, setError] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setIsLoading(true);

      const response = await apiFetch(
        '/api/ingestion/jobs/'
      );

      const data = await response.json();

      setJobs(data);
    } catch (err) {
      setError('Failed to load jobs.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpand = async (jobId: string) => {
    if (expandedJobId === jobId) {
      setExpandedJobId(null);

      return;
    }

    setExpandedJobId(jobId);

    if (!jobRows[jobId]) {
      setLoadingRows(jobId);

      try {
        const response = await apiFetch(
          `/api/ingestion/jobs/${jobId}/rows/`
        );

        const data = await response.json();

        setJobRows((prev) => ({
          ...prev,
          [jobId]: data,
        }));
      } catch (err) {
        console.error('Failed to load rows');
      } finally {
        setLoadingRows(null);
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done':
        return (
          <Check className="w-4 h-4 text-emerald-500" />
        );

      case 'failed':
        return (
          <AlertCircle className="w-4 h-4 text-red-500" />
        );

      case 'processing':
        return (
          <Loader className="w-4 h-4 text-yellow-500 animate-spin" />
        );

      default:
        return (
          <Clock className="w-4 h-4 text-gray-500" />
        );
    }
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">
            Import Jobs
          </h1>

          <p className="text-gray-400">
            Track the status of your data import jobs
          </p>
        </div>

        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-24">
              <div className="text-center">
                <Loader className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-4" />

                <p className="text-gray-400">
                  Loading jobs...
                </p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-24">
              <p className="text-red-400">{error}</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 px-4">
              <Clock className="w-8 h-8 text-gray-500 mb-4" />

              <h3 className="text-lg font-medium text-white mb-2">
                No import jobs yet
              </h3>

              <p className="text-gray-400 text-center max-w-sm">
                Upload a file to create your first import
                job.
              </p>
            </div>
          ) : (
            <>
              <div className="bg-gray-800/50 px-6 py-4 border-b border-gray-800">
                <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-400">
                  <div className="col-span-1"></div>

                  <div className="col-span-3">
                    Filename
                  </div>

                  <div className="col-span-2">
                    Source Type
                  </div>

                  <div className="col-span-2">
                    Status
                  </div>

                  <div className="col-span-1 text-center">
                    Rows
                  </div>

                  <div className="col-span-1 text-center">
                    Errors
                  </div>

                  <div className="col-span-2">
                    Date
                  </div>
                </div>
              </div>

              <div className="divide-y divide-gray-800">
                {jobs.map((job) => (
                  <div key={job.id}>
                    <button
                      onClick={() =>
                        toggleExpand(job.id)
                      }
                      className="w-full px-6 py-4 hover:bg-gray-800/50 transition-colors"
                    >
                      <div className="grid grid-cols-12 gap-4 items-center text-sm">
                        <div className="col-span-1">
                          {expandedJobId === job.id ? (
                            <ChevronUp className="w-5 h-5 text-gray-400" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-gray-400" />
                          )}
                        </div>

                        <div className="col-span-3 text-white font-medium text-left">
                          {job.raw_filename}
                        </div>

                        <div className="col-span-2 text-gray-300 text-left">
                          {job.source_type}
                        </div>

                        <div className="col-span-2">
                          <StatusBadge
                            status={job.status}
                          />
                        </div>

                        <div className="col-span-1 text-center text-gray-300">
                          {job.row_count.toLocaleString()}
                        </div>

                        <div className="col-span-1 text-center">
                          {job.error_count > 0 ? (
                            <span className="text-red-400 font-medium">
                              {job.error_count}
                            </span>
                          ) : (
                            <span className="text-gray-500">
                              0
                            </span>
                          )}
                        </div>

                        <div className="col-span-2 text-gray-400 text-left">
                          {new Date(
                            job.created_at
                          ).toLocaleString()}
                        </div>
                      </div>
                    </button>

                    {expandedJobId === job.id && (
                      <div className="bg-gray-800/30 px-6 py-4 border-t border-gray-800">
                        <div className="ml-4">
                          <h4 className="text-sm font-medium text-gray-400 mb-3">
                            Ingestion Row Details
                          </h4>

                          {loadingRows === job.id ? (
                            <div className="flex items-center gap-2 text-gray-400">
                              <Loader className="w-4 h-4 animate-spin" />

                              <span className="text-sm">
                                Loading rows...
                              </span>
                            </div>
                          ) : (
                            <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
                              <div className="max-h-64 overflow-y-auto">
                                <table className="w-full">
                                  <thead className="bg-gray-800/50 sticky top-0">
                                    <tr>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                                        Row
                                      </th>

                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                                        Status
                                      </th>

                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                                        Error
                                      </th>
                                    </tr>
                                  </thead>

                                  <tbody className="divide-y divide-gray-800">
                                    {(
                                      jobRows[
                                        job.id
                                      ] || []
                                    ).map((row) => (
                                      <tr
                                        key={row.id}
                                        className="hover:bg-gray-800/30"
                                      >
                                        <td className="px-4 py-3 text-sm text-gray-300">
                                          {
                                            row.row_index
                                          }
                                        </td>

                                        <td className="px-4 py-3">
                                          <div className="flex items-center gap-2">
                                            {getStatusIcon(
                                              row.status
                                            )}

                                            <StatusBadge
                                              status={
                                                row.status
                                              }
                                            />
                                          </div>
                                        </td>

                                        <td className="px-4 py-3 text-sm">
                                          {row.error_message ? (
                                            <span className="text-red-400">
                                              {
                                                row.error_message
                                              }
                                            </span>
                                          ) : (
                                            <span className="text-gray-500">
                                              -
                                            </span>
                                          )}
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}