import { Sidebar } from "./sidebar";
import { TopNav } from "./top-nav";

export function Shell({
  children,
  title,
  subtitle,
  dataSource,
  status,
  platform,
}: {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  dataSource?: string;
  status?: string;
  platform?: string;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopNav title={title} subtitle={subtitle} dataSource={dataSource} status={status} platform={platform} />
        <main className="flex-1 p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
