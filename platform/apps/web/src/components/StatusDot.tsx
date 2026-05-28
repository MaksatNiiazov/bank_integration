import type { ServiceStatus } from '../lib/types';

const statusLabel: Record<ServiceStatus, string> = {
  ok: 'Работает',
  unavailable: 'Недоступен',
  unknown: 'Неизвестно',
};

export function StatusDot({ status }: { status: ServiceStatus }) {
  return (
    <span className={`status-dot status-${status}`}>
      <span aria-hidden="true" />
      {statusLabel[status]}
    </span>
  );
}
