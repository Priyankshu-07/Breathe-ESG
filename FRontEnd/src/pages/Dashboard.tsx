import React, { useState, useMemo, useEffect } from 'react';
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

import { apiFetch } from '../api/client';

type EmissionStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'flagged';

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
  const [selectedIds, setSelectedIds] = useState<Set<string>>(
    new Set()
  );

  const [isProcessing, setIsProcessing] = useState(false);

  const [filterScope, setFilterScope] =
    useState<string>('all');

  const [filterStatus, setFilterStatus] =
    useState<string>('all');

  const [searchTerm, setSearchTerm] = useState('');

  const [emissions, setEmissions] = useState<Emission[]>(
    []
  );

  const [isLoadingData, setIsLoadingData] =
    useState(true);

  useEffect(() => {
    fetchEmissions();
  }, []);

  const fetchEmissions = async () => {
    try {
      setIsLoadingData(true);

      const response = await apiFetch(
        '/api/emissions/'
      );

      const data = await response.json();

      const mapped = data.map((e: any) => ({
        id: e.id,

        category: e.category,

        scope:
          e.scope === 'scope1'
            ? 'Scope 1'
            : e.scope === 'scope2'
            ? 'Scope 2'
            : 'Scope 3',

        activityValue: parseFloat(e.activity_value),

        co2e: e.co2e_kg
          ? parseFloat(e.co2e_kg)
          : 0,

        period: `${e.period_start} → ${e.period_end}`,

        source: e.source_type,

        status:
          e.status === 'pending_review'
            ? 'pending'
            : e.status,

        errorMessage: e.warnings,
      }));

      setEmissions(mapped);
    } catch (err) {
      console.error('Failed to load emissions');
    } finally {
      setIsLoadingData(false);
    }
  };

  // Summary Stats
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

    const pendingCount = emissions.filter(
      (e) => e.status === 'pending'
    ).length;

    const approvedCount = emissions.filter(
      (e) => e.status === 'approved'
    ).length;

    const rejectedCount = emissions.filter(
      (e) => e.status === 'rejected'
    ).length;

    const flaggedCount = emissions.filter(
      (e) => e.status === 'flagged'
    ).length;

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
      const matchesScope =
        filterScope === 'all' ||
        e.scope === filterScope;

      const matchesStatus =
        filterStatus === 'all' ||
        e.status === filterStatus;

      const matchesSearch =
        searchTerm === '' ||
        e.category
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        e.source
          .toLowerCase()
          .includes(searchTerm.toLowerCase());

      return (
        matchesScope &&
        matchesStatus &&
        matchesSearch
      );
    });
  }, [
    emissions,
    filterScope,
    filterStatus,
    searchTerm,
  ]);

  const handleSelectAll = () => {
    if (
      selectedIds.size ===
      filteredEmissions.length
    ) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(
        new Set(filteredEmissions.map((e) => e.id))
      );
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

  const handleApprove = async (id: string) => {
    try {
      await apiFetch(
        `/api/review/${id}/approve/`,
        {
          method: 'POST',
        }
      );

      setEmissions((prev) =>
        prev.map((e) =>
          e.id === id
            ? {
                ...e,
                status:
                  'approved' as EmissionStatus,
              }
            : e
        )
      );
    } catch (err) {
      console.error('Approve failed');
    }
  };

  const handleReject = async (id: string) => {
    try {
      await apiFetch(
        `/api/review/${id}/reject/`,
        {
          method: 'POST',
          body: JSON.stringify({
            note: '',
          }),
        }
      );

      setEmissions((prev) =>
        prev.map((e) =>
          e.id === id
            ? {
                ...e,
                status:
                  'rejected' as EmissionStatus,
              }
            : e
        )
      );
    } catch (err) {
      console.error('Reject failed');
    }
  };

  const handleFlag = async (id: string) => {
    try {
      await apiFetch(
        `/api/review/${id}/flag/`,
        {
          method: 'POST',
          body: JSON.stringify({
            note: '',
          }),
        }
      );

      setEmissions((prev) =>
        prev.map((e) =>
          e.id === id
            ? {
                ...e,
                status:
                  'flagged' as EmissionStatus,
              }
            : e
        )
      );
    } catch (err) {
      console.error('Flag failed');
    }
  };

  const handleBulkApprove = async () => {
    try {
      await apiFetch(
        '/api/review/bulk/',
        {
          method: 'POST',
          body: JSON.stringify({
            emission_ids:
              Array.from(selectedIds),

            action: 'approve',
          }),
        }
      );

      setEmissions((prev) =>
        prev.map((e) =>
          selectedIds.has(e.id)
            ? {
                ...e,
                status:
                  'approved' as EmissionStatus,
              }
            : e
        )
      );

      setSelectedIds(new Set());
    } catch (err) {
      console.error(
        'Bulk approve failed'
      );
    }
  };

  const handleBulkReject = async () => {
    try {
      await apiFetch(
        '/api/review/bulk/',
        {
          method: 'POST',
          body: JSON.stringify({
            emission_ids:
              Array.from(selectedIds),

            action: 'reject',
          }),
        }
      );

      setEmissions((prev) =>
        prev.map((e) =>
          selectedIds.has(e.id)
            ? {
                ...e,
                status:
                  'rejected' as EmissionStatus,
              }
            : e
        )
      );

      setSelectedIds(new Set());
    } catch (err) {
      console.error(
        'Bulk reject failed'
      );
    }
  };

  const handleLockForAudit = async () => {
    try {
      setIsProcessing(true);

      const response = await apiFetch(
        '/api/review/lock/',
        {
          method: 'POST',
        }
      );

      const data = await response.json();

      alert(
        data.detail || 'Locked for audit.'
      );

      fetchEmissions();
    } catch (err) {
      alert('Lock failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const canBulkApprove = useMemo(() => {
    return Array.from(selectedIds).some(
      (id) => {
        const emission = emissions.find(
          (e) => e.id === id
        );

        return (
          emission?.status === 'pending' ||
          emission?.status === 'flagged'
        );
      }
    );
  }, [selectedIds, emissions]);

  return (
    <Layout>
      <div className="p-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Review Dashboard
            </h1>

            <p className="text-gray-400">
              Review and approve emissions
              data
            </p>
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

        {isLoadingData ? (
          <div className="flex items-center justify-center py-32">
            <Loader className="w-8 h-8 text-emerald-500 animate-spin" />
          </div>
        ) : (
          <>
            {/* REST OF YOUR EXISTING JSX REMAINS SAME */}
          </>
        )}
      </div>
    </Layout>
  );
}