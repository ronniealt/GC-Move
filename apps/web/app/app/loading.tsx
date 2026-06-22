export default function Loading() {
  return (
    <div className="flex items-center justify-center h-64">
      <div
        className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin"
        style={{ borderColor: "#4A9B8E", borderTopColor: "transparent" }}
      />
    </div>
  );
}
