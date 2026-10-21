const form=document.getElementById("loginForm"), status=document.getElementById("status");
const anonId=(crypto.randomUUID?crypto.randomUUID():"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,c=>{const r=Math.random()*16|0;return(c==="x"?r:(r&3|8)).toString(16)})).toLowerCase();
async function logEvent(type){
 const name=document.getElementById("participantName").value.trim(), code=document.getElementById("participantCode").value.trim();
 if(!name||!code){status.textContent="Enter your name and participant code first.";return false}
 if(!document.getElementById("consent").checked){status.textContent="Please consent to activity logging.";return false}
 try{
  const r=await fetch("/api/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({consent:true,event_type:type,participant_name:name,participant_code:code,anon_id:anonId})});
  if(!r.ok){status.textContent="Could not record event. Please try again.";return false} return true
 }catch(_){status.textContent="Connection issue. Please try again.";return false}
}
form.addEventListener("submit",async e=>{e.preventDefault();/* Never read or transmit demo username/password values. */if(await logEvent("demo_started"))location.href="/lesson"});
document.getElementById("revealBtn").addEventListener("click",async()=>{if(await logEvent("lesson_completed"))location.href="/lesson"});
