const $=s=>document.querySelector(s), drop=$("#drop"), picker=$("#file");
const show=id=>["drop","progress","done","error"].forEach(x=>$("#"+x).hidden=x!==id);
$("#choose").onclick=()=>picker.click(); picker.onchange=()=>picker.files[0]&&upload(picker.files[0]);
["dragenter","dragover"].forEach(e=>drop.addEventListener(e,x=>{x.preventDefault();drop.classList.add("over")}));
["dragleave","drop"].forEach(e=>drop.addEventListener(e,x=>{x.preventDefault();drop.classList.remove("over")}));
drop.addEventListener("drop",e=>e.dataTransfer.files[0]&&upload(e.dataTransfer.files[0]));
["retry","another"].forEach(id=>$("#"+id).onclick=()=>{picker.value="";show("drop")});
async function upload(file){show("progress");$("#filename").textContent=file.name;$("#stage").textContent="Uploading TTML";const body=new FormData();body.append("file",file);try{const r=await fetch("/api/jobs",{method:"POST",body});const data=await r.json();if(!r.ok)throw Error(data.detail||"Upload failed");poll(data.id)}catch(e){fail(e.message)}}
async function poll(id){try{const r=await fetch(`/api/jobs/${id}`),job=await r.json();if(!r.ok)throw Error(job.detail||"Status unavailable");$("#stage").textContent=job.stage;if(job.status==="complete")return finish(id,job);if(job.status==="failed")return fail(job.error);setTimeout(()=>poll(id),1200)}catch(e){fail(e.message)}}
function finish(id,job){show("done");$("#doneTitle").textContent=job.sourceFilename;$("#counts").innerHTML=Object.entries(job.counts||{}).map(([k,v])=>`<span>${v} ${k}</span>`).join("");$("#view").href=`/api/jobs/${id}/report`;$("#view").target="_blank";$("#download").href=`/api/jobs/${id}/download/report`}
function fail(message){show("error");$("#errorText").textContent=message||"An unexpected error occurred."}
