import React, { useState, useEffect } from 'react';
import {
  ChevronDown,
  ChevronUp,
  FileJson,
  Loader,
  Filter,
} from 'lucide-react';

import Layout from '../components/Layout';

import { useAuth } from '../contexts/AuthContext';
import { apiFetch } from '../api/client';

interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  detail: Record<string, any>;
}

export default function Audit() {
  const { token } = useAuth();

  const [expandedId, setExpandedId] = useState<
    string | null
  >(null);

  const [auditEntries, setAuditEntries] = useState<
    AuditEntry[]
  >([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [filterAction, setFilterAction] =
    useState<string>('all');

  const [searchActor, setSearchActor] =
    useState('');

  useEffect(() => {
    fetchAudit();
  }, []);

  const fetchAudit = async () => {
    try {
      setIsLoading(true);

      const response = await apiFetch(
        '/api/audit/',
        token
      );

      const data = await response.json();

      const mapped = data.map((e: any) => ({
        id: e.id,

        timestamp: new Date(
          e.timestamp
        ).toLocaleString(),

        actor: e.actor || 'system',

        action: e.verb,

        detail: e.detail,
      }));

      setAuditEntries(mapped);
    } catch (err) {
      console.error(
        'Failed to load audit log'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(
      expandedId === id ? null : id
    );
  };

  // Unique Actions
  const uniqueActions = Array.from(
    new Set(
      auditEntries.map(
        (entry) => entry.action
      )
    )
  );

  // Filter Entries
  const filteredEntries = auditEntries.filter(
    (entry) => {
      const matchesAction =
        filterAction === 'all' ||
        entry.action === filterAction;

      const matchesActor =
        searchActor === '' ||
        entry.actor
          .toLowerCase()
          .includes(
            searchActor.toLowerCase()
          );

      return (
        matchesAction && matchesActor
      );
    }
  );

  return (
    <Layout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">
            Audit Log
          </h1>

          <p className="text-gray-400">
            Track all actions and changes
            in the system
          </p>
        </div>

        {/* Filters */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />

              <span className="text-sm text-gray-400">
                Filters:
              </span>
            </div>

            {/* Actor Search */}
            <div className="flex-1 min-w-48">
              <input
                type="text"
                placeholder="Search by actor..."
                value={searchActor}
                onChange={(e) =>
                  setSearchActor(
                    e.target.value
                  )
                }
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            {/* Action Filter */}
            <select
              value={filterAction}
              onChange={(e) =>
                setFilterAction(
                  e.target.value
                )
              }
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="all">
                All Actions
              </option>

              {uniqueActions.map(
                (action) => (
                  <option
                    key={action}
                    value={action}
                  >
                    {action}
                  </option>
                )
              )}
            </select>
          </div>
        </div>

        {/* Audit Table */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          {/* Loading */}
          {isLoading ? (
            <div className="flex items-center justify-center py-24">
              <div className="text-center">
                <Loader className="w-8 h-8 text-emerald-500 animate-spin mx-auto mb-4" />

                <p className="text-gray-400">
                  Loading audit log...
                </p>
              </div>
            </div>
          ) : filteredEntries.length ===
            0 ? (
            /* Empty State */
            <div className="flex flex-col items-center justify-center py-24 px-4">
              <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mb-4">
                <FileJson className="w-8 h-8 text-gray-500" />
              </div>

              <h3 className="text-lg font-medium text-white mb-2">
                No audit entries found
              </h3>

              <p className="text-gray-400 text-center max-w-sm">
                Try adjusting your
                filters or search
                terms.
              </p>
            </div>
          ) : (
            <>
              {/* Table Header */}
              <div className="bg-gray-800/50 px-6 py-4 border-b border-gray-800">
                <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-400">
                  <div className="col-span-1"></div>

                  <div className="col-span-2">
                    Timestamp
                  </div>

                  <div className="col-span-3">
                    Actor
                  </div>

                  <div className="col-span-3">
                    Action
                  </div>

                  <div className="col-span-3">
                    Detail
                  </div>
                </div>
              </div>

              {/* Audit Entries */}
              <div className="divide-y divide-gray-800">
                {filteredEntries.map(
                  (entry) => (
                    <div key={entry.id}>
                      {/* Row */}
                      <button
                        onClick={() =>
                          toggleExpand(
                            entry.id
                          )
                        }
                        className="w-full px-6 py-4 hover:bg-gray-800/50 transition-colors text-left"
                      >
                        <div className="grid grid-cols-12 gap-4 items-center text-sm">
                          <div className="col-span-1">
                            {expandedId ===
                            entry.id ? (
                              <ChevronUp className="w-5 h-5 text-gray-400" />
                            ) : (
                              <ChevronDown className="w-5 h-5 text-gray-400" />
                            )}
                          </div>

                          <div className="col-span-2 text-gray-400">
                            {
                              entry.timestamp
                            }
                          </div>

                          <div className="col-span-3 text-white font-medium">
                            {entry.actor}
                          </div>

                          <div className="col-span-3">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700">
                              {
                                entry.action
                              }
                            </span>
                          </div>

                          <div className="col-span-3 text-gray-400 truncate">
                            {getActionSummary(
                              entry
                            )}
                          </div>
                        </div>
                      </button>

                      {/* Expanded */}
                      {expandedId ===
                        entry.id && (
                        <div className="bg-gray-800/30 px-6 py-4 border-t border-gray-800">
                          <div className="ml-4">
                            <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                              <FileJson className="w-4 h-4" />
                              Detail JSON
                            </h4>

                            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 overflow-x-auto">
                              <pre className="text-sm text-gray-300 font-mono whitespace-pre">
                                {JSON.stringify(
                                  entry.detail,
                                  null,
                                  2
                                )}
                              </pre>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}

function getActionSummary(
  entry: AuditEntry
): string {
  const detail = entry.detail;

  switch (entry.action) {
    case 'Approved Emission':
    case 'Rejected Emission':
    case 'Flagged Emission':
      return `${detail.category} (${detail.scope})`;

    case 'Data Imported':
      return `${detail.filename} - ${detail.totalRows} rows`;

    case 'Locked for Audit':
      return `${detail.period} - ${detail.emissionsLocked} records`;

    case 'Bulk Approved':
      return `${detail.count} emissions approved`;

    case 'User Login':
      return `IP: ${detail.ipAddress}`;

    default:
      return '-';
  }
}