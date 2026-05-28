import React from 'react';

type Status = 'done' | 'failed' | 'processing' | 'pending' | 'approved' | 'rejected' | 'flagged';

interface StatusBadgeProps {
  status: Status;
}

const statusStyles: Record<Status, string> = {
  done: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  approved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  rejected: 'bg-red-500/20 text-red-400 border-red-500/30',
  processing: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  flagged: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  pending: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

const statusLabels: Record<Status, string> = {
  done: 'Done',
  failed: 'Failed',
  processing: 'Processing',
  pending: 'Pending',
  approved: 'Approved',
  rejected: 'Rejected',
  flagged: 'Flagged',
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusStyles[status]}`}
    >
      {statusLabels[status]}
    </span>
  );
}
