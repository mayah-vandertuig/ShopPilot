import { Sidebar } from "./sidebar";
import { TopNav } from "./top-nav";

export function Shell({ children, title, dataSource }: { children: React.ReactNode; title?: string; dataSource?: string }) {
  return (
    <div className="flex min-h-screen bg-muted/30">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <TopNav title={title} dataSource={dataSource} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
