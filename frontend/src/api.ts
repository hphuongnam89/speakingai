export class ApiError extends Error {
  status:number;
  constructor(status:number, message:string) { super(message); this.status=status; }
}

export function errorMessage(body:unknown):string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as {detail:unknown}).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return "Kiểm tra lại các trường đã nhập.";
  }
  return "Không thể hoàn thành yêu cầu. Hãy thử lại.";
}

export async function api<T>(path:string, options:RequestInit = {}, profile?:string):Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type","application/json");
  if (profile) headers.set("X-Profile-Id",profile);
  let response:Response;
  try { response = await fetch("/api/v1"+path,{...options,headers,credentials:"same-origin",signal:options.signal ?? AbortSignal.timeout(100000)}); }
  catch { throw new ApiError(0,"Không kết nối được máy chủ hoặc yêu cầu quá lâu. Bản nháp vẫn được giữ trên màn hình."); }
  const payload:unknown = await response.json();
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") window.dispatchEvent(new Event("session-expired"));
    throw new ApiError(response.status, response.status === 401 ? "Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại." : errorMessage(payload));
  }
  return payload as T;
}

export const post = (body:unknown):RequestInit => ({method:"POST",body:JSON.stringify(body)});
