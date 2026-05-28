import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, Check, Clock, Loader } from 'lucide-react';
import Layout from '../components/Layout';
import StatusBadge from '../components/StatusBadge';
import { jobsData } from '../data/placeholderData';

type JobStatus = 'done' | 'failed' | 'processing' | 'pending';

interface IngestionRow {
  rowIndex: number;
  status: JobStatus;
  errorMessage?: string;
}

interface Job {
  id: string;
  filename: string;
  sourceType: string;
  status: JobStatus;
  totalRows: number;
  errors: number;
  date: string;
  ingestionRows: IngestionRow[];
}

export default function Jobs() {
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [isLoading] = useState(false);

  const toggleExpand = (jobId: string) => {
    setExpandedJobId(expandedJobId === jobId ? null : jobId);
  };

  const getStatusIcon = (status: JobStatus) => {
    switch (status) {
      case 'done':
        return <Check className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'processing':
        return <Loader className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <Layout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">Import Jobs</h1>
          <p className="text-gray-400">Track the status of your data import jobs</p>
        </div>

        {/* Jobs Table */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center justify-center py-24">
              <div className="text-center">
                <Loader className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Loading jobs...</p>
              </div>
            </div>
          ) : jobsData.length === 0 ? (
            /* Empty State */
            <div className="flex flex-col items-center justify-center py-24 px-4">
              <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mb-4">
                <Clock className="w-8 h-8 text-gray-500" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No import jobs yet</h3>
              <p className="text-gray-400 text-center max-w-sm">
                Upload a file to create your first import job. Jobs will appear here for tracking.
              </p>
            </div>
          ) : (
            <>
              {/* Table Header */}
              <div className="bg-gray-800/50 px-6 py-4 border-b border-gray-800">
                <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-400">
                  <div className="col-span-1"></div>
                  <div className="col-span-3">Filename</div>
                  <div className="col-span-2">Source Type</div>
                  <div className="col-span-2">Status</div>
                  <div className="col-span-1 text-center">Rows</div>
                  <div className="col-span-1 text-center">Errors</div>
                  <div className="col-span-2">Date</div>
                </div>
              </div>

              {/* Job Rows */}
              <div className="divide-y divide-gray-800">
                {(jobsData as Job[]).map((job) => (
                  <div key={job.id}>
                    {/* Job Row */}
                    <button
                      onClick={() => toggleExpand(job.id)}
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
                        <div className="col-span-3 text-white font-medium">
                          {job.filename}
                        </div>
                        <div className="col-span-2 text-gray-300">{job.sourceType}</div>
                        <div className="col-span-2">
                          <StatusBadge status={job.status} />
                        </div>
                        <div className="col-span-1 text-center text-gray-300">
                          {job.totalRows.toLocaleString()}
                        </div>
                        <div className="col-span-1 text-center">
                          {job.errors > 0 ? (
                            <span className="text-red-400 font-medium">{job.errors}</span>
                          ) : (
                            <span className="text-gray-500">0</span>
                          )}
                        </div>
                        <div className="col-span-2 text-gray-400">{job.date}</div>
                      </div>
                    </button>

                    {/* Expanded Details */}
                    {expandedJobId === job.id && (
                      <div className="bg-gray-800/30 px-6 py-4 border-t border-gray-800">
                        <div className="ml-4">
                          <h4 className="text-sm font-medium text-gray-400 mb-3">
                            Ingestion Row Details
                          </h4>
                          <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
                            <div className="max-h-64 overflow-y-auto">
                              <table className="w-full">
                                <thead className="bg-gray-800/50 sticky top-0">
                                  <tr>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                                      Row Index
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                                      Status
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                                      Error Message
                                    </th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-800">
                                  {job.ingestionRows.map((row, idx) => (
                                    <tr key={idx} className="hover:bg-gray-800/30">
                                      <td className="px-4 py-3 text-sm text-gray-300">
                                        {row.rowIndex}
                                      </td>
                                      <td className="px-4 py-3">
                                        <div className="flex items-center gap-2">
                                          {getStatusIcon(row.status)}
                                          <StatusBadge status={row.status} />
                                        </div>
                                      </td>
                                      <td className="px-4 py-3 text-sm">
                                        {row.errorMessage ? (
                                          <span className="text-red-400">
                                            {row.errorMessage}
                                          </span>
                                        ) : (
                                          <span className="text-gray-500">-</span>
                                        )}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
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
