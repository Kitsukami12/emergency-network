// @ts-nocheck
import React, { useState } from 'react';
// @ts-nocheck
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchAccidents, patchAccidentStatus } from '../api/client';
import type { Accident } from '../api/types';

import { colors } from '../theme';

// Simple mock detection: when a video is uploaded we create a new accident with status NEEDS_VERIFICATION
const uploadVideo = async (file: File) => {
  // In mock mode the backend will treat this as a new accident via the existing endpoint.
  // Here we just resolve after a short delay.
  await new Promise((r) => setTimeout(r, 500));
  return true;
};

export default function CameraDetection() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedAccident, setSelectedAccident] = useState<Accident | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation((f: File) => uploadVideo(f), {
    onSuccess: () => {
      queryClient.invalidateQueries(['accidents']);
    },
  });

  const verifyMutation = useMutation(
    ({ id, status }: { id: string; status: string }) => patchAccidentStatus(id, status),
    {
      onSuccess: () => queryClient.invalidateQueries(['accidents']),
    },
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };

  const handleUpload = () => {
    if (file) uploadMutation.mutate(file);
  };

  // Pull list of accidents needing verification for display
  const { data: accidents = [], isLoading } = useQuery(['accidents'], fetchAccidents);
  const pending = accidents.filter((a) => a.status === 'NEEDS_VERIFICATION');

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl" style={{ color: colors.accent }}>Camera & Detection</h2>
      <div className="flex flex-col gap-2">
        <input type="file" accept="video/*" onChange={handleFileChange} />
        <button
          className="px-4 py-2 rounded bg-accent text-black disabled:opacity-50"
          onClick={handleUpload}
          disabled={!file || uploadMutation.isLoading}
        >
          {uploadMutation.isLoading ? 'Uploading…' : 'Upload Video'}
        </button>
      </div>

      <section className="border border-border rounded bg-panel p-2 max-h-64 overflow-auto">
        <h3 className="text-lg font-semibold mb-2" style={{ color: colors.accent }}>Needs‑Verification Queue</h3>
        {isLoading ? (
          <p className="text-gray-400">Loading…</p>
        ) : pending.length === 0 ? (
          <p className="text-gray-400">No pending detections.</p>
        ) : (
          <ul className="space-y-2">
            {pending.map((a) => (
              <li key={a.accident_id} className="p-2 rounded" style={{ backgroundColor: '#222' }}>
                <strong>{a.accident_id}</strong> – {a.severity}
                <div className="mt-1 flex gap-2">
                  <button
                    className="px-2 py-1 rounded bg-low text-black"
                    onClick={() => verifyMutation.mutate({ id: a.accident_id, status: 'AWAITING_AMBULANCE' })}
                  >
                    Confirm
                  </button>
                  <button
                    className="px-2 py-1 rounded bg-critical text-black"
                    onClick={() => verifyMutation.mutate({ id: a.accident_id, status: 'CANCELLED' })}
                  >
                    Dismiss
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
