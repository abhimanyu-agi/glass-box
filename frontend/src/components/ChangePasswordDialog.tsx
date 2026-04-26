import { useState } from "react";
import type { FormEvent } from "react";
import { X, KeyRound } from "lucide-react";
import { changePassword } from "@/lib/api";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function ChangePasswordDialog({ open, onClose }: Props) {
  const [current, setCurrent]   = useState("");
  const [next, setNext]         = useState("");
  const [confirm, setConfirm]   = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [success, setSuccess]   = useState(false);

  if (!open) return null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (next !== confirm) {
      setError("New passwords don't match.");
      return;
    }
    if (next.length < 6) {
      setError("New password must be at least 6 characters.");
      return;
    }
    if (next === current) {
      setError("New password must differ from current password.");
      return;
    }

    setSubmitting(true);
    try {
      await changePassword(current, next);
      setSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 1400);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Failed to change password.");
    } finally {
      setSubmitting(false);
    }
  }

  function handleClose() {
    setCurrent("");
    setNext("");
    setConfirm("");
    setError(null);
    setSuccess(false);
    setSubmitting(false);
    onClose();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-foreground/30 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-xl shadow-xl w-full max-w-sm">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-brand-50 dark:bg-brand-600/15 flex items-center justify-center">
              <KeyRound className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
            </div>
            <p className="text-sm font-semibold text-foreground">Change password</p>
          </div>
          <button
            onClick={handleClose}
            className="w-7 h-7 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition flex items-center justify-center"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-3">
          <Field label="Current password" id="cur">
            <input
              id="cur"
              type="password"
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
              required
              autoFocus
              className={inputClass}
            />
          </Field>

          <Field label="New password" id="new">
            <input
              id="new"
              type="password"
              value={next}
              onChange={(e) => setNext(e.target.value)}
              required
              minLength={6}
              className={inputClass}
              placeholder="At least 6 characters"
            />
          </Field>

          <Field label="Confirm new password" id="conf">
            <input
              id="conf"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={6}
              className={inputClass}
            />
          </Field>

          {error && (
            <div className="rounded-md bg-destructive/10 text-destructive text-sm px-3 py-2 border border-destructive/20">
              {error}
            </div>
          )}

          {success && (
            <div className="rounded-md bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 text-sm px-3 py-2 border border-emerald-500/20">
              Password updated successfully.
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              className="flex-1 py-2 rounded-md border border-border text-foreground text-sm font-medium hover:bg-muted transition disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || success}
              className="flex-1 py-2 rounded-md bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium transition disabled:opacity-50"
            >
              {submitting ? "Updating..." : success ? "Updated" : "Update"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const inputClass =
  "w-full px-3 py-2 rounded-md border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-brand-600 focus:border-transparent transition";

function Field({ label, id, children }: { label: string; id: string; children: React.ReactNode }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-foreground mb-1.5">
        {label}
      </label>
      {children}
    </div>
  );
}