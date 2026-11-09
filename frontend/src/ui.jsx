export const card = 'rounded-2xl border border-slate-200/80 bg-white shadow-card'

export const input =
  'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-[inset_0_1px_2px_rgb(15_23_42/0.04)] outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100'

export const button =
  'inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'

export const outline =
  'inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-[inset_0_1px_2px_rgb(15_23_42/0.04)] transition hover:border-indigo-300 hover:bg-indigo-50/60 hover:text-indigo-900 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:ring-offset-2'

export function Panel({ title, subtitle, children, action }) {
  return (
    <section className={`${card} p-5`}>
      {(title || action) && (
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-base font-semibold text-slate-900">{title}</h2>}
            {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}

export function Title({ children }) {
  return (
    <div className="mb-5 border-b border-slate-200 pb-4">
      <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{children}</h1>
    </div>
  )
}

export function Chip({ children }) {
  return <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-800">{children}</span>
}

export function StatCard({ label, value, hint }) {
  return (
    <div className={`${card} p-5`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  )
}

export function DataTable({ headers, rows }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="bg-slate-50">
            {headers.map((item) => (
              <th key={item} className="border-b border-slate-200 px-3 py-2.5 font-semibold text-slate-500">
                {item}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} className="transition-colors hover:bg-slate-50/70">
              {row.map((value, cell) => (
                <td key={cell} className="border-b border-slate-100 px-3 py-2.5 align-top text-slate-700">
                  {value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
