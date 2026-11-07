import {useEffect,useRef,useState} from "react";
import {api,post} from "./api";

export function SpeakingRecorder({attempt,profile,onTranscript}:{attempt:string;profile:string;onTranscript:(text:string,turn:string)=>void}) {
  const recorder=useRef<MediaRecorder|null>(null), stream=useRef<MediaStream|null>(null);
  const timer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined);
  const [recording,setRecording]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState(""),[audio,setAudio]=useState("");
  useEffect(()=>()=>{clearTimeout(timer.current);if(recorder.current){recorder.current.onstop=null;if(recorder.current.state==="recording")recorder.current.stop();}stream.current?.getTracks().forEach(t=>t.stop());},[]);
  useEffect(()=>()=>{if(audio)URL.revokeObjectURL(audio);},[audio]);
  async function start(){
    setError("");
    try {
      if(!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder)throw new Error("Trình duyệt chưa hỗ trợ ghi âm; bạn có thể gõ câu trả lời.");
      const input=await navigator.mediaDevices.getUserMedia({audio:true});stream.current=input;
      const rec=new MediaRecorder(input),chunks:BlobPart[]=[];recorder.current=rec;
      rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
      rec.onstop=async()=>{
        clearTimeout(timer.current);
        input.getTracks().forEach(t=>t.stop());setRecording(false);setBusy(true);
        const blob=new Blob(chunks,{type:rec.mimeType});setAudio(URL.createObjectURL(blob));
        try {
          const session=await api<{session_id:string}>(`/learning/attempts/${attempt}/speaking-session`,post({}),profile);
          const data=new FormData();data.append("session_id",session.session_id);data.append("audio",blob,rec.mimeType.includes("mp4")?"recording.mp4":"recording.webm");
          const result=await api<{text:string;turn_id:string}>("/speech/transcribe",{method:"POST",body:data},profile);
          onTranscript(result.text,result.turn_id);
        }catch(e){setError((e as Error).message+" Bạn vẫn có thể nghe bản ghi và gõ/sửa transcript.");}finally{setBusy(false);}
      };
      rec.start();setRecording(true);timer.current=setTimeout(()=>{if(rec.state==="recording")rec.stop();},180000);
    }catch(e){stream.current?.getTracks().forEach(t=>t.stop());setError((e as Error).message);}
  }
  return <section aria-label="Ghi âm bài nói"><p>Nói hết ý rồi dừng để nhận transcript. Bạn có thể sửa lỗi nhận dạng trước khi nộp.</p><button type="button" disabled={busy} onClick={()=>recording?recorder.current?.stop():start()}>{busy?"Đang nhận dạng…":recording?"Dừng ghi âm":"Ghi câu trả lời"}</button>{audio&&<audio controls src={audio}/>}<p role="status">{recording?"Đang ghi âm — tối đa 3 phút.":""}</p>{error&&<p role="alert" className="error">{error}</p>}</section>;
}
