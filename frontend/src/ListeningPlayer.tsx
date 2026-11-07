import {useState} from "react";
import {api,post} from "./api";

export function ListeningPlayer({url,attempt,step,profile,onRevision}:{url:string;attempt:string;step:string;profile:string;onRevision:(revision:number)=>void}){
  const [transcript,setTranscript]=useState(""),[error,setError]=useState(""),[plays,setPlays]=useState(0);
  async function exposure(kind:"transcript"|"replay"){
    try{const r=await api<{transcript:string|null;revision:number}>(`/learning/attempts/${attempt}/exposure`,post({request_id:crypto.randomUUID(),step_id:step,kind}),profile);onRevision(r.revision);if(r.transcript)setTranscript(r.transcript);}catch(e){setError((e as Error).message);}
  }
  return <section><p>Audio tổng hợp · Bản nháp chờ kiểm duyệt. Có thể dừng và nghe lại để học.</p><audio controls preload="metadata" src={url+"?preview=true"} onPlay={()=>{if(plays)exposure("replay");setPlays(plays+1);}} onError={()=>setError("Audio chưa sẵn sàng. Hãy thử tải lại bài.")}/><button className="text-button" onClick={()=>exposure("transcript")}>Xem transcript (ghi nhận trợ giúp)</button>{transcript&&<blockquote>{transcript}</blockquote>}{error&&<p role="alert" className="error">{error}</p>}</section>;
}
