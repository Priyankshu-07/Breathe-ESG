import React, { useState, useMemo } from 'react';
import {
  CheckCircle,
  XCircle,
  Flag,
  Lock,
  Leaf,
  Zap,
  Truck,
  AlertCircle,
  Loader,
} from 'lucide-react';
import Layout from '../components/Layout';
import StatusBadge from '../components/StatusBadge';
import { emissionsData } from '../data/placeholderData';

type EmissionStatus = 'pending' | 'approved' | 'rejected' | 'flagged';

interface Emission {
  id: string;
  category: string;
  scope: string;
  activityValue: number;
  co2e: number;
  period: string;
  source: string;
  status: EmissionStatus;
  errorMessage?: string;
  flagReason?: string;
}

export default function Dashboard() {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isProcessing, setIsProcessing] = useState(false);
  const [filterScope, setFilterScope] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [emissions, setEmissions] = useState<Emission[]>(emissionsData as Emission[]);

  // Calculate summary stats
  const stats = useMemo(() => {
    const scope1Total = emissions
      .filter((e) => e.scope === 'Scope 1')
      .reduce((sum, e) => sum + e.co2e, 0);

    const scope2Total = emissions
      .filter((e) => e.scope === 'Scope 2')
      .reduce((sum, e) => sum + e.co2e, 0);

    const scope3Total = emissions
      .filter((e) => e.scope === 'Scope 3')
      .reduce((sum, e) => sum + e.co2e, 0);

    const pendingCount = emissions.filter((e) => e.status === 'pending').length;
    const approvedCount = emissions.filter((e) => e.status === 'approved').length;
    const rejectedCount = emissions.filter((e) => e.status === 'rejected').length;
    const flaggedCount = emissions.filter((e) => e.status === 'flagged').length;

    return {
      scope1Total,
      scope2Total,
      scope3Total,
      pendingCount,
      approvedCount,
      rejectedCount,
      flaggedCount,
    };
  }, [emissions]);

  // Filter emissions
  const filteredEmissions = useMemo(() => {
    return emissions.filter((e) => {
      const matchesScope = filterScope === 'all' || e.scope === filterScope;
      const matchesStatus = filterStatus === 'all' || e.status === filterStatus;
      const matchesSearch =
        searchTerm === '' ||
        e.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.source.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesScope && matchesStatus && matchesSearch;
    });
  }, [emissions, filterScope, filterStatus, searchTerm]);

  const handleSelectAll = () => {
    if (selectedIds.size === filteredEmissions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredEmissions.map((e) => e.id)));
    }
  };

  const handleSelectOne = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const updateStatus = async (ids: string[], newStatus: EmissionStatus) => {
    setIsProcessing(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setEmissions((prev) =>
      prev.map((e) => (ids.includes(e.id) ? { ...e, status: newStatus } : e))
    );
    setSelectedIds(new Set());
    setIsProcessing(false);
  };

  const handleApprove = (id: string) => updateStatus([id], 'approved');
  const handleReject = (id: string) => updateStatus([id], 'rejected');
  const handleFlag = (id: string) => updateStatus([id], 'flagged');

  const handleBulkApprove = () => {
    const pendingOrFlagged = Array.from(selectedIds).filter((id) => {
      const emission = emissions.find((e) => e.id === id);
      return emission?.status === 'pending' || emission?.status === 'flagged';
    });
    if (pendingOrFlagged.length > 0) {
      updateStatus(pendingOrFlagged, 'approved');
    }
  };

  const handleBulkReject = () => {
    if (selectedIds.size > 0) {
      updateStatus(Array.from(selectedIds), 'rejected');
    }
  };

  const handleLockForAudit = async () => {
    setIsProcessing(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsProcessing(false);
    alert('Audit period locked successfully!');
  };

  const canBulkApprove = useMemo(() => {
    return Array.from(selectedIds).some((id) => {
      const emission = emissions.find((e) => e.id === id);
      return emission?.status === 'pending' || emission?.status === 'flagged';
    });
  }, [selectedIds, emissions]);

  return (
    <Layout>
      <div className="p-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Review Dashboard</h1>
            <p className="text-gray-400">Review and approve emissions data</p>
          </div>
          <button
            onClick={handleLockForAudit}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            <Lock className="w-4 h-4" />
            Lock for Audit
          </button>
        </div>

        {/* Scope Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Scope 1 */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                <Leaf className="w-6 h-6 text-emerald-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Scope 1</p>
                <p className="text-white font-medium">Direct Emissions</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-white">
              {stats.scope1Total.toLocaleString()}
              <span className="text-lg font-normal text-gray-400 ml-2">kg CO2e</span>
            </p>
          </div>

          {/* Scope 2 */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Zap className="w-6 h-6 text-blue-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Scope 2</p>
                <p className="text-white font-medium">Indirect - Energy</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-white">
              {stats.scope2Total.toLocaleString()}
              <span className="text-lg font-normal text-gray-400 ml-2">kg CO2e</span>
            </p>
          </div>

          {/* Scope 3 */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center">
                <Truck className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Scope 3</p>
                <p className="text-white font-medium">Value Chain</p>
              </div>
            </div>
            <p className="text-3xl font-bold text-white">
              {stats.scope3Total.toLocaleString()}
              <span className="text-lg font-normal text-gray-400 ml-2">kg CO2e</span>
            </p>
          </div>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gray-500/20 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-gray-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.pendingCount}</p>
              <p className="text-gray-400 text-sm">Pending</p>
            </div>
          </div>

          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.approvedCount}</p>
              <p className="text-gray-400 text-sm">Approved</p>
            </div>
          </div>

          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.rejectedCount}</p>
              <p className="text-gray-400 text-sm">Rejected</p>
            </div>
          </div>

          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
              <Flag className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.flaggedCount}</p>
              <p className="text-gray-400 text-sm">Flagged</p>
            </div>
          </div>
        </div>

        {/* Filters and Bulk Actions */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="flex-1 min-w-64">
              <input
                type="text"
                placeholder="Search by category or source..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            {/* Scope Filter */}
            <select
              value={filterScope}
              onChange={(e) => setFilterScope(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="all">All Scopes</option>
              <option value="Scope 1">Scope 1</option>
              <option value="Scope 2">Scope 2</option>
              <option value="Scope 3">Scope 3</option>
            </select>

            {/* Status Filter */}
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="flagged">Flagged</option>
            </select>

            {/* Bulk Actions */}
            {selectedIds.size > 0 && (
              <>
                <button
                  onClick={handleBulkApprove}
                  disabled={!canBulkApprove || isProcessing}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  {isProcessing ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <CheckCircle className="w-4 h-4" />
                  )}
                  Bulk Approve ({selectedIds.size})
                </button>
                <button
                  onClick={handleBulkReject}
                  disabled={isProcessing}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  {isProcessing ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <XCircle className="w-4 h-4" />
                  )}
                  Bulk Reject ({selectedIds.size})
                </button>
              </>
            )}
          </div>
        </div>

        {/* Emissions Table */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          {filteredEmissions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 px-4">
              <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mb-4">
                <AlertCircle className="w-8 h-8 text-gray-500" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No emissions found</h3>
              <p className="text-gray-400 text-center max-w-sm">
                Try adjusting your filters or search terms.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800/50">
                  <tr>
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedIds.size === filteredEmissions.length && filteredEmissions.length > 0}
                        onChange={handleSelectAll}
                        className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-emerald-500 focus:ring-emerald-500"
                      />
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                      Category
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                      Scope
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400">
                      Activity Value
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400">
                      CO2e (kg)
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                      Period
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                      Source
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {filteredEmissions.map((emission) => {
                    const isFlagged = emission.status === 'flagged';
                    const isError = emission.status === 'rejected';
                    return (
                      <tr
                        key={emission.id}
                        className={`hover:bg-gray-800/50 transition-colors ${
                          isFlagged ? 'bg-yellow-500/10' : isError ? 'bg-red-500/10' : ''
                        }`}
                      >
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            checked={selectedIds.has(emission.id)}
                            onChange={() => handleSelectOne(emission.id)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-emerald-500 focus:ring-emerald-500"
                          />
                        </td>
                        <td className="px-4 py-3 text-white text-sm">{emission.category}</td>
                        <td className="px-4 py-3 text-gray-300 text-sm">{emission.scope}</td>
                        <td className="px-4 py-3 text-gray-300 text-sm text-right">
                          {emission.activityValue.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-white text-sm text-right font-medium">
                          {emission.co2e.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-gray-300 text-sm">{emission.period}</td>
                        <td className="px-4 py-3 text-gray-300 text-sm">{emission.source}</td>
                        <td className="px-4 py-3">
                          <StatusBadge status={emission.status} />
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {(emission.status === 'pending' || emission.status === 'flagged') && (
                              <button
                                onClick={() => handleApprove(emission.id)}
                                disabled={isProcessing}
                                className="p-1 text-emerald-500 hover:bg-emerald-500/20 rounded transition-colors disabled:opacity-50"
                                title="Approve"
                              >
                                <CheckCircle className="w-4 h-4" />
                              </button>
                            )}
                            {emission.status !== 'rejected' && (
                              <button
                                onClick={() => handleReject(emission.id)}
                                disabled={isProcessing}
                                className="p-1 text-red-500 hover:bg-red-500/20 rounded transition-colors disabled:opacity-50"
                                title="Reject"
                              >
                                <XCircle className="w-4 h-4" />
                              </button>
                            )}
                            {(emission.status === 'pending' || emission.status === 'flagged') && (
                              <button
                                onClick={() => handleFlag(emission.id)}
                                disabled={isProcessing}
                                className="p-1 text-yellow-500 hover:bg-yellow-500/20 rounded transition-colors disabled:opacity-50"
                                title="Flag"
                              >
                                <Flag className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
