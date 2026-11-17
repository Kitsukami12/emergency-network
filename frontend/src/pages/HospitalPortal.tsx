// src/pages/HospitalPortal.tsx
// @ts-nocheck
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchHospitals, fetchNotifications, updateNotificationStatus } from '../api/client';
import { Hospital, Notification, Severity } from '../api/types';
import { colors } from '../theme';

export default function HospitalPortal() {
  const queryClient = useQueryClient();
  const { data: hospitals = [], isLoading: hLoading } = useQuery(['hospitals'], fetchHospitals);
  const [selectedHospital, setSelectedHospital] = useState<string | null>(null);

  const { data: notifications = [], isLoading: nLoading } = useQuery(
    ['notifications', selectedHospital],
    () => fetchNotifications(selectedHospital ?? undefined),
    { enabled: !!selectedHospital },
  );

  const ackMutation = useMutation(
    ({ id }: { id: string }) => updateNotificationStatus(id, 'ACKNOWLEDGED'),
    { onSuccess: () => queryClient.invalidateQueries(['notifications']) },
  );

  const acceptMutation = useMutation(
    ({ id }: { id: string }) => updateNotificationStatus(id, 'ACCEPTED'),
    { onSuccess: () => queryClient.invalidateQueries(['notifications']) },
  );

  const statusColor = (severity: Severity) => {
    switch (severity) {
      case 'LOW':
        return colors.low;
      case 'MEDIUM':
        return colors.medium;
      case 'HIGH':
        return colors.high;
      case 'CRITICAL':
        return colors.critical;
      default:
        return colors.border;
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl" style={{ color: colors.accent }}>Hospital Portal</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {/* Hospital selector */}
        <section className="border border-border rounded bg-panel p-2">
          <h3 className="font-semibold mb-2" style={{ color: colors.accent }}>Select Hospital</h3>
          {hLoading ? (
            <p className="text-gray-400">Loading…</p>
          ) : (
            <select
              className="w-full p-2 rounded bg-background text-white"
              value={selectedHospital ?? ''}
              onChange={(e) => setSelectedHospital(e.target.value || null)}
            >
              <option value="">-- Choose --</option>
              {hospitals.map((h) => (
                <option key={h.hospital_id} value={h.hospital_id}>
                  {h.name}
                </option>
              ))}
            </select>
          )}
        </section>
        {/* Notifications */}
        <section className="border border-border rounded bg-panel p-2 max-h-96 overflow-auto">
          <h3 className="font-semibold mb-2" style={{ color: colors.accent }}>Incoming Notifications</h3>
          {nLoading ? (
            <p className="text-gray-400">Loading…</p>
          ) : notifications.length === 0 ? (
            <p className="text-gray-400">No notifications.</p>
          ) : (
            <ul className="space-y-2">
              {notifications.map((n) => (
                <li key={n.notification_id} className="p-2 rounded" style={{ backgroundColor: statusColor(n.severity) + '20' }}>
                  <strong>{n.accident_id}</strong> – {n.severity}
                  <div className="mt-1 flex gap-2">
                    <button
                      className="px-2 py-1 rounded bg-low text-black"
                      onClick={() => ackMutation.mutate({ id: n.notification_id })}
                    >
                      Acknowledge
                    </button>
                    <button
                      className="px-2 py-1 rounded bg-accent text-black"
                      onClick={() => acceptMutation.mutate({ id: n.notification_id })}
                    >
                      Prepare Bay
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
