import React, {useEffect,useState,useRef} from "react";
import {createRoot} from "react-dom/client";
import {api,post,ApiError} from "./api";
import "./style.css";
import {ListeningPlayer} from "./ListeningPlayer";
import {SpeakingRecorder} from "./SpeakingRecorder";

type Profile={id:string;name:string};
type Lesson={id:string;version:string;title:string;skill:string;objective:string;status:string;estimated_minutes:number;steps:Step[]};
type Step={id:string;kind:string;instruction:string;stimulus:string;audio_url?:string;items:{id:string;prompt:string}[]};
type Feedback={explanation?:string;next_action?:string;hint?:string;result?:string;learner_text?:string;answer?:string;evidence?:string;evidence_kind?:string;source_step_id?:string;claim_type?:string;criteria?:string[];annotations?:{quote:string;comment:string}[];revision:number};
type Attempt={id:string;lesson_id:string;version:string;step_id:string;draft:string;drafts:Record<string,string>;revision:number;events:{action:string;result:Feedback}[]};
type Recommendation={kind:string;lesson_id:string;version:string;item_id?:string;step_id?:string;review_id?:string;reason:string;state:string};
type Today={date:string;explanation:string;recommendations:Recommendation[];competencies:{lesson_id:string;skill:string;objective:string;state:string;independent_items:number;transfer_items:number;retention_items:number}[];blockers:{lesson_id:string;reason:string}[]};
const labels:Record<string,string>={explain:"Hiểu mục tiêu",worked_example:"Xem cách làm",guided:"Thử với gợi ý",independent:"Tự thực hiện",feedback:"Nhìn lại phản hồi",self_repair:"Tự sửa",transfer:"Vận dụng mới",review:"Củng cố"};
const skillNames:Record<string,string>={reading:"ĐỌC HIỂU",listening:"NGHE HIỂU",writing:"VIẾT RÕ Ý",speaking:"NÓI TỰ TIN"};

function Auth({onLogin}:{onLogin:()=>void}) {
  const [register,setRegister]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState("");
  async function authenticate(event:React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();setBusy(true);setError("");
    const data=new FormData(event.currentTarget);
    try {await api("/auth/"+(register?"register":"login"),{...post({email:data.get("email"),password:data.get("password")}),headers:{"X-Browser-Session":"true"}});onLogin();}
    catch(e){setError((e as Error).message);}finally{setBusy(false);}
  }
  return <main className="auth-layout"><section><p className="eyebrow">SPEAKWELL / LEARNING EDITION</p><h1>Hiểu sâu hơn.<br/>Dùng tiếng Anh<br/><em>tự tin hơn.</em></h1><p className="intro">Từng mục tiêu nhỏ, từng lần tự sửa. Học cách nghe, đọc, viết và nói bằng ý của chính bạn.</p><div className="principles"><span>01 · Hiểu</span><span>02 · Thực hành</span><span>03 · Vận dụng</span></div></section>
    <section className="auth-card"><h2>{register?"Tạo tài khoản học tập":"Tiếp tục hành trình"}</h2><p>Dùng cùng tài khoản và hồ sơ cho bài học và Speaking.</p><form onSubmit={authenticate}><label>Email<input name="email" type="email" required autoComplete="username"/></label><label>Mật khẩu<input name="password" type="password" minLength={10} maxLength={128} required autoComplete={register?"new-password":"current-password"}/></label>{error&&<p role="alert" className="error">{error}</p>}<button disabled={busy}>{busy?"Đang xử lý…":register?"Tạo tài khoản":"Đăng nhập"}</button></form><button className="text-button" onClick={()=>{setRegister(!register);setError("");}}>{register?"Đã có tài khoản? Đăng nhập":"Chưa có tài khoản? Tạo tài khoản"}</button><p className="fine">Dữ liệu học lưu trên máy chủ của bạn. Không cần tài khoản dịch vụ AI để bắt đầu.</p></section></main>;
}

function LessonPlayer({lesson,attempt:initial,profile,onBack,target}:{lesson:Lesson;attempt:Attempt;profile:string;onBack:()=>void;target?:Recommendation}) {
  const [attempt,setAttempt]=useState(initial),[draft,setDraft]=useState(initial.draft),[stepId,setStepId]=useState(initial.step_id);
  const [itemId,setItemId]=useState(""),[evidence,setEvidence]=useState(initial.drafts[`${initial.step_id}:evidence`]??""),[busy,setBusy]=useState(false),[error,setError]=useState(""),[saved,setSaved]=useState("Đã khôi phục bài học");
  const [feedback,setFeedback]=useState<Feedback|null>(initial.events.at(-1)?.result??null),[question,setQuestion]=useState(""),[turnId,setTurnId]=useState<string|undefined>();
  const requestIds=useRef(new Map<string,string>());
  const current=useRef(initial),pendingSave=useRef<Promise<Attempt>>(Promise.resolve(initial));
  const index=Math.max(0,lesson.steps.findIndex(s=>s.id===stepId)),step=lesson.steps[index];
  useEffect(()=>{setItemId(target?.step_id===step.id?target.item_id??step.items[0]?.id??"":step.items[0]?.id??"");setEvidence(current.current.drafts[`${step.id}:evidence`]??"");setTurnId(undefined);},[step.id]);
  function save(nextStep=stepId,text=draft,nextItem=nextStep===stepId?itemId:undefined,nextEvidence=evidence) {
    const task=pendingSave.current.catch(()=>current.current).then(async()=>{
      const updated=await api<Attempt>(`/learning/attempts/${current.current.id}`,{method:"PATCH",body:JSON.stringify({expected_revision:current.current.revision,step_id:nextStep,draft:text,item_id:nextItem||undefined,evidence:nextEvidence})},profile);
      current.current=updated;setAttempt(updated);setSaved("Đã lưu");return updated;
    });
    pendingSave.current=task;return task;
  }
  useEffect(()=>{
    if((draft===attempt.draft&&evidence===(attempt.drafts[`${stepId}:evidence`]??""))||busy)return;
    const timer=setTimeout(()=>{save().catch(e=>{setError(e.message);setSaved("Chưa lưu — giữ nguyên bản nháp");});},1500);
    return()=>clearTimeout(timer);
  },[draft,evidence,attempt.revision,busy]);
  async function navigate(next:number) {
    setBusy(true);setError("");
    try{const updated=await save();const target=lesson.steps[next].id;const nextDraft=updated.drafts[target]??"";await save(target,nextDraft,undefined,updated.drafts[`${target}:evidence`]??"");setDraft(nextDraft);setStepId(target);setItemId(lesson.steps[next].items[0]?.id??"");setFeedback(null);}
    catch(e){setError((e as Error).message);}finally{setBusy(false);}
  }
  async function act(kind:"submit"|"hints"|"tutor"|"feedback") {
    setBusy(true);setError("");
    try {
      const current=await save();
      const action={step_id:stepId,...(kind==="feedback"?{item_id:itemId}:{}),...(kind==="submit"?{item_id:itemId,text:draft,turn_id:turnId,...(lesson.skill==="reading"?{evidence}: {})}:{}),...(kind==="tutor"?{question}: {})};
      const key=kind+JSON.stringify(action);if(!requestIds.current.has(key))requestIds.current.set(key,crypto.randomUUID());
      const body={request_id:requestIds.current.get(key),...action};
      const result=await api<Feedback>(`/learning/attempts/${current.id}/${kind}`,post(body),profile);
      setFeedback(result);const refreshed=await api<Attempt>(`/learning/attempts/${current.id}`,{},profile);currentRefreshed(refreshed);
    }catch(e){setError((e as Error).message);}finally{setBusy(false);}
  }
  useEffect(()=>{current.current=attempt;},[attempt]);
  async function changeItem(id:string){setBusy(true);try{const updated=await save();const text=updated.drafts[`${stepId}:${id}`]??"";await save(stepId,text,id,"");setItemId(id);setDraft(text);setEvidence("");setFeedback(null);setTurnId(undefined);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
  function currentRefreshed(row:Attempt){current.current=row;setAttempt(row);pendingSave.current=Promise.resolve(row);}
  async function reloadSaved(){setBusy(true);try{const row=await api<Attempt>(`/learning/attempts/${attempt.id}`,{},profile);current.current=row;pendingSave.current=Promise.resolve(row);setAttempt(row);setError("");setSaved("Đã tải phiên bản lưu; câu trả lời trên màn hình vẫn giữ để bạn đối chiếu.");}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
  return <main className="lesson-layout"><aside><button className="text-button" disabled={busy} onClick={async()=>{try{await save();onBack();}catch(e){setError((e as Error).message);}}}>← Bài học hôm nay</button><p className="eyebrow">{skillNames[lesson.skill]}</p><h2>{lesson.title}</h2><ol className="step-list">{lesson.steps.map((s,i)=><li key={s.id}><button aria-current={s.id===stepId?"step":undefined} disabled={busy} onClick={()=>navigate(i)}><span>{String(i+1).padStart(2,"0")}</span>{labels[s.kind]}</button></li>)}</ol><p className="fine">Đã xem bài chưa đồng nghĩa đã thành thạo. Hệ thống ghi riêng mức trợ giúp và lần tự thực hiện.</p></aside>
    <section className="lesson-content"><p className="eyebrow">BƯỚC {index+1} / {lesson.steps.length} · {labels[step.kind]}</p><h1>{lesson.objective}</h1>{lesson.status!=="published"&&<p className="draft-banner">BẢN NHÁP · Chưa có người duyệt nội dung. Dùng để thử luồng học, chưa phát hành như giáo trình chuẩn.</p>}
    {step.audio_url&&<ListeningPlayer key={step.id} url={step.audio_url} attempt={attempt.id} step={step.id} profile={profile} onRevision={revision=>{current.current={...current.current,revision};setAttempt(current.current);}}/>}{lesson.skill==="listening"&&!step.audio_url&&step.stimulus&&<p className="notice">Phiên bản cũ chỉ có kịch bản đọc thử.</p>}{lesson.skill==="speaking"&&step.items.length>0&&<SpeakingRecorder key={step.id} attempt={attempt.id} profile={profile} onTranscript={(text,turn)=>{setDraft(text);setTurnId(turn);}}/>}
    <p className="instruction">{step.instruction}</p>{step.stimulus&&<blockquote>{step.stimulus}</blockquote>}
    {step.items.length>0&&<><label>Nhiệm vụ<select value={itemId} disabled={busy} onChange={e=>changeItem(e.target.value)}>{step.items.map(i=><option key={i.id} value={i.id}>{i.prompt}</option>)}</select></label><label>Câu trả lời của bạn<textarea value={draft} disabled={busy} rows={5} onChange={e=>{setDraft(e.target.value);setSaved("Đang chờ lưu…");}} placeholder="Hãy diễn đạt bằng lời của bạn…"/></label>{lesson.skill==="reading"&&<label>Bằng chứng trong đoạn (tuỳ chọn)<textarea value={evidence} disabled={busy} rows={3} onChange={e=>setEvidence(e.target.value)} placeholder="Chọn hoặc chép phần câu làm căn cứ…"/></label>}<div className="actions"><button disabled={busy||!draft.trim()} onClick={()=>act("submit")}>Nộp để nhận phản hồi</button><button className="secondary" disabled={busy} onClick={()=>act("hints")}>Cho tôi một gợi ý</button></div></>}
    <div className="save-line" role="status">{busy?"Đang xử lý…":saved}</div>{error&&<div role="alert" className="error">{error}<button className="text-button" onClick={reloadSaved} disabled={busy}>Tải trạng thái đã lưu để thử lại</button></div>}
    {feedback&&<section className="feedback" aria-live="polite"><p className="eyebrow">PHẢN HỒI ĐỂ HỌC</p>{feedback.hint&&<p>{feedback.hint}</p>}{feedback.result&&<p>{feedback.result==="met"?"Bạn đã xác định đúng thông tin.":feedback.result==="not_yet"?"Hãy xem lại bằng chứng và thử tự sửa.":"Đã lưu câu trả lời; chưa kết luận năng lực."}</p>}{feedback.answer&&<p>Đáp án của câu đã nộp: <strong>{feedback.answer}</strong></p>}{feedback.evidence&&<blockquote>{feedback.evidence}</blockquote>}{feedback.explanation&&<p>{feedback.explanation}</p>}{feedback.next_action&&<p>{feedback.next_action}</p>}{feedback.source_step_id&&<small>Nguồn trong bài: {feedback.source_step_id}</small>}{feedback.evidence_kind&&<small>Loại ghi nhận: {feedback.evidence_kind}. Chưa phải kết luận thành thạo.</small>}</section>}
    {['writing','speaking'].includes(lesson.skill)&&step.items.length>0&&<button className="secondary" disabled={busy} onClick={()=>act("feedback")}>Nhận góp ý theo mục tiêu cho bài đã nộp</button>}
    {feedback?.claim_type&&<p>{({error:"Lỗi cần xem lại",suggestion:"Gợi ý tuỳ chọn — không bắt buộc đổi câu đúng",valid_alternative:"Cách diễn đạt hợp lệ",explanation:"Giải thích"} as Record<string,string>)[feedback.claim_type]}</p>}{feedback?.criteria?.map((c,i)=><p key={i}>{c}</p>)}{feedback?.annotations?.map((a,i)=><blockquote key={i}>“{a.quote}” — {a.comment}</blockquote>)}
    {step.kind==='self_repair'&&<details><summary>Đối chiếu bản gốc và bản tự sửa</summary>{attempt.events.filter(e=>e.action==='submit').map((e,i)=><blockquote key={i}>{e.result.learner_text??"Bản gốc nằm trong lịch sử phiên trước."}</blockquote>)}<p>Bản đang sửa: {draft}</p></details>}
    {!['independent','transfer','review'].includes(step.kind)&&<form className="tutor" onSubmit={e=>{e.preventDefault();act("tutor");}}><label>Hỏi Tutor về bài đang học<input value={question} maxLength={2000} onChange={e=>setQuestion(e.target.value)} placeholder="Tôi chưa hiểu vì sao…"/></label><button className="secondary" disabled={busy||!question.trim()}>Giải thích và hướng dẫn tôi tự sửa</button></form>}
    <nav className="actions"><button className="secondary" disabled={busy||index===0} onClick={()=>navigate(index-1)}>← Trước</button><button disabled={busy||index===lesson.steps.length-1} onClick={()=>navigate(index+1)}>Bước tiếp theo →</button></nav></section></main>;
}

function App(){
  const [signedIn,setSignedIn]=useState<boolean|null>(null),[profiles,setProfiles]=useState<Profile[]>([]),[profile,setProfile]=useState("");
  const [lessons,setLessons]=useState<Lesson[]>([]),[active,setActive]=useState<{lesson:Lesson;attempt:Attempt;target?:Recommendation}|null>(null);
  const [minutes,setMinutes]=useState(20),[refresh,setRefresh]=useState(0);
  const [today,setToday]=useState<Today|null>(null);
  const [preview,setPreview]=useState(false),[dev,setDev]=useState(false),[error,setError]=useState(""),[busy,setBusy]=useState(false);
  const [models,setModels]=useState<string[]>([]),[model,setModel]=useState("");
  useEffect(()=>{api("/auth/session").then(()=>setSignedIn(true)).catch(()=>setSignedIn(false));const expired=()=>{setSignedIn(false);setProfiles([]);setProfile("");setActive(null);};window.addEventListener("session-expired",expired);return()=>window.removeEventListener("session-expired",expired);},[]);
  async function loadProfiles(){const ps=await api<Profile[]>("/profiles");setProfiles(ps);setProfile(ps[0]?.id??"");}
  useEffect(()=>{if(!signedIn)return;loadProfiles().catch(e=>setError(e.message));api<{environment:string}>("/info").then(info=>setDev(info.environment==="development")).catch(e=>setError(e.message));},[signedIn]);
  useEffect(()=>{if(!profile)return;let cancelled=false;setError("");setLessons([]);setToday(null);Promise.all([api<{lessons:Lesson[]}>("/learning/units?preview="+preview,{},profile),api<{installed_models:string[];selected_model:string}>("/models",{},profile),api<Today>(`/learning/today?preview=${preview}&minutes=${minutes}`,{},profile)]).then(([catalog,status,plan])=>{if(!cancelled){setLessons(catalog.lessons);setModels(status.installed_models);setModel(status.selected_model);setToday(plan);}}).catch(e=>{if(!cancelled)setError(e.message);});return()=>{cancelled=true;};},[profile,preview,minutes,refresh]);
  async function openLesson(lesson:Lesson,target?:Recommendation){
    setBusy(true);setError("");
    try{
      const content=await api<Lesson>(`/learning/lessons/${lesson.id}?version=${encodeURIComponent(lesson.version)}&preview=${preview}`,{},profile);
      const history=await api<Attempt[]>("/learning/attempts",{},profile),prior=history.find(a=>a.lesson_id===lesson.id&&a.version===lesson.version);
      let attempt=prior?await api<Attempt>(`/learning/attempts/${prior.id}`,{},profile):await api<Attempt>(`/learning/attempts?preview=${preview}`,post({lesson_id:lesson.id,version:lesson.version,request_id:crypto.randomUUID()}),profile);
      if(target?.kind==="review"&&target.step_id)attempt=await api<Attempt>(`/learning/attempts/${attempt.id}`,{method:"PATCH",body:JSON.stringify({expected_revision:attempt.revision,step_id:target.step_id,draft:attempt.drafts[target.step_id]??""})},profile);
      setActive({lesson:content,attempt,target});
    }catch(e){setError((e as Error).message);}finally{setBusy(false);}
  }
  async function postpone(review:string){try{await api(`/learning/reviews/${review}/reschedule`,post({days:1}),profile);setRefresh(v=>v+1);}catch(e){setError((e as Error).message);}}
  async function changeProfile(value:string){setBusy(true);try{await api(`/profiles/${value}/select`,post({}));setProfile(value);setActive(null);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
  async function createProfile(e:React.SubmitEvent<HTMLFormElement>){e.preventDefault();setBusy(true);try{const name=new FormData(e.currentTarget).get("name");await api("/profiles",post({name}));await loadProfiles();}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
  async function selectModel(value:string){setBusy(true);try{await api("/models/select",post({model:value,preference:"local_only"}),profile);setModel(value);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
  if(signedIn===null)return <main><p role="status">Đang khôi phục phiên học…</p></main>;
  if(!signedIn)return <Auth onLogin={()=>setSignedIn(true)}/>;
  return <><header><a className="brand" href="/learn">speakwell<span>LEARN. USE. GROW.</span></a><nav><a href="/speaking">Phòng Speaking ↗</a><label>Hồ sơ<select aria-label="Hồ sơ học viên" value={profile} disabled={busy||!!active} onChange={e=>changeProfile(e.target.value)}>{profiles.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><button className="text-button" onClick={async()=>{await api("/auth/logout",post({}));setSignedIn(false);setActive(null);setProfile("");}}>Đăng xuất</button></nav></header>
  {active?<LessonPlayer key={active.attempt.id} lesson={active.lesson} attempt={active.attempt} target={active.target} profile={profile} onBack={()=>{setActive(null);setRefresh(v=>v+1);}}/>:<main className="home"><p className="eyebrow">MỖI NGÀY, MỘT ĐIỀU LÀM ĐƯỢC</p><h1>Học để hiểu.<br/><em>Luyện để dùng được.</em></h1><p className="intro">Bắt đầu từ một mục tiêu vừa sức. Hiểu cách làm, tự thử, rồi vận dụng trong một tình huống mới.</p>{error&&<p role="alert" className="error">{error}</p>}
  <label>Thời gian hôm nay<select value={minutes} onChange={e=>setMinutes(Number(e.target.value))}>{[10,20,30].map(n=><option key={n} value={n}>{n} phút</option>)}</select></label>
  {today&&<section className="today-card"><p className="eyebrow">TODAY · {today.date}</p><h2>Hôm nay nên làm gì?</h2><p>{today.explanation}</p>{today.recommendations.map((r,i)=><div className="today-row" key={`${r.lesson_id}-${r.item_id||r.step_id}`}><span>{i+1}</span><div><strong>{r.kind==="review"?"Ôn lại":r.kind==="practice"?"Tiếp tục":"Bài mới"}</strong><p>{r.reason}</p></div><button className="secondary" disabled={busy} onClick={()=>{const lesson=lessons.find(l=>l.id===r.lesson_id&&l.version===r.version)??{id:r.lesson_id,version:r.version} as Lesson;openLesson(lesson,r);}}>Mở bài →</button>{r.review_id&&<button className="text-button" onClick={()=>postpone(r.review_id!)}>Dời 1 ngày</button>}</div>)}{today.blockers.map(b=><p className="notice" key={b.lesson_id}>{b.reason}</p>)}{!today.recommendations.length&&<p>Chưa có hoạt động phù hợp; xem mục tiêu và lịch ôn bên dưới.</p>}</section>}
  {today&&<section><h2>Điều bạn đang luyện</h2><div className="lesson-grid">{today.competencies.map(c=><article className="lesson-card" key={c.lesson_id}><p className="eyebrow">{skillNames[c.skill]}</p><h3>{c.objective}</h3><p>{({not_started:"Chưa có bằng chứng",learning:"Đang học có hỗ trợ",practicing:"Đang tự thực hiện",provisionally_mastered:"Tạm đạt mục tiêu — chờ ôn",needs_review:"Cần ôn lại"} as Record<string,string>)[c.state]}</p><small>Tự thực hiện: {c.independent_items} · Vận dụng: {c.transfer_items} · Ôn đạt: {c.retention_items}</small></article>)}</div></section>}
  {!profiles.length?<form className="auth-card" onSubmit={createProfile}><h2>Bạn muốn được gọi là gì?</h2><label>Tên hồ sơ<input name="name" required minLength={1} maxLength={50}/></label><button disabled={busy}>Tạo hồ sơ học tập</button></form>:<><section className="unit-heading"><div><p className="eyebrow">ĐƠN VỊ HỌC ĐẦU TIÊN</p><h2>Thay đổi kế hoạch,<br/>giải thích lựa chọn.</h2></div><p>Nghe và đọc để hiểu ý.<br/>Viết và nói bằng lời của mình.</p></section>
  {dev&&<label className="preview-toggle"><input type="checkbox" checked={preview} onChange={e=>setPreview(e.target.checked)}/> Xem bài nháp để thử luồng học (chưa kiểm duyệt)</label>}
  {!lessons.length&&<p className="notice">Chưa có bài đã phát hành. {dev?"Bạn có thể bật xem bài nháp ở trên để thử nền tảng.":"Nội dung đang chờ kiểm duyệt."}</p>}
  <div className="lesson-grid">{lessons.map((l,i)=><article className="lesson-card" key={l.id+l.version}><p className="eyebrow">{String(i+1).padStart(2,"0")} / {skillNames[l.skill]}</p><h3>{l.title}</h3><p>{l.objective}</p><div className="card-foot"><small>Khoảng {l.estimated_minutes} phút · {l.status==="draft"?"Bản nháp":"Bài học"}</small><button disabled={busy} onClick={()=>openLesson(l)}>Vào học →</button></div></article>)}</div>
  <section className="model-settings"><h2>AI trên máy của bạn</h2><p>Chỉ liệt kê model đã cài. Tutor dùng local; không tự tải model hoặc gửi bài lên cloud.</p><label>Model cho hồ sơ này<select aria-label="Model AI" value={model} disabled={busy} onChange={e=>selectModel(e.target.value)}>{!models.includes(model)&&<option value={model}>{model} — chưa thấy trên máy</option>}{models.map(m=><option key={m}>{m}</option>)}</select></label></section></>}
  </main>}<footer>Speakwell Learning Edition · Học, tự sửa và vận dụng · Preview 0.2</footer></>;
}

createRoot(document.getElementById("root")!).render(<App/>);
