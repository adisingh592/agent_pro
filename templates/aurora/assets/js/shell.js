/* Personal Agent Aurora · by fls-dev · https://github.com/fls-dev */
/* ==========================================================================
   Personal Agent · shell.js — app shell bootstrap
   J.shell(title) builds the shared chrome on every page:
     aurora + dots + vignette + grain, top bar (crumb · status · ⌘K · bell ·
     New task · avatar), wheel (desktop) + dock/radial (tablet/mobile),
     ⌘K palette, and enhances <aside class="inspector"> if present.
   J.ready(fn)  run fn after fonts are loaded and layout is stable (use it
                for anything that measures DOM, e.g. edges).
   toast(title,sub,icon,color,ms)  glass notification, bottom-right.
   ========================================================================== */
function toast(title,sub,icon='check',color='var(--ok)',ms=4200){let c=$('#toasts');if(!c){c=document.createElement('div');c.className='toasts';c.id='toasts';document.body.appendChild(c)}
 const t=document.createElement('div');t.className='toast g3';t.innerHTML=`<span class="ti" style="background:color-mix(in srgb,${color} 18%,transparent);color:${color}">${ico(icon,17,2)}</span><div><b>${title}</b><small>${sub}</small></div>`;c.appendChild(t);
 if(ms)setTimeout(()=>{t.style.transition='opacity .4s,transform .4s';t.style.opacity=0;t.style.transform='translateY(8px)';setTimeout(()=>t.remove(),400)},ms);return t}
J.ready=fn=>document.fonts.ready.then(()=>requestAnimationFrame(()=>requestAnimationFrame(fn)));
J.shell=function(title){
 const b=document.body;
 b.insertAdjacentHTML('afterbegin','<div class="aurora" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div class="dots" aria-hidden="true"></div><div class="vignette" aria-hidden="true"></div>');
 b.insertAdjacentHTML('beforeend','<div class="grain" aria-hidden="true"></div>');
 const t=document.createElement('header');t.className='topbar';
 t.innerHTML=`<div class="g3" style="gap:10px">
  <a class="crumb g3" href="../../index.html" title="Main Hub"><span class="mo"></span><b>Personal Agent</b></a>
  <span style="opacity:.3">/</span>
  <span class="crumb g3" style="color:var(--ink-2)">${title}</span>
 </div>
  <div class="status g3"><span><span class="dot"></span><b>SYS</b> online</span><i></i><span>Windows <b>11</b></span><i class="opt"></i><span class="opt">GPU <b>RTX 3050</b></span><i></i><span>Ollama <b>ready</b></span></div>
  <button class="kbtn g3" id="kOpen" aria-label="Command palette">${ico('search',16)}<span class="t">Ask or jump</span><kbd>⌘K</kbd></button>
  <button class="bell g3" aria-label="Notifications">${ico('bell',18)}<i></i></button>
  <a class="btn btn-glass" style="height:42px;display:inline-flex;align-items:center;padding:0 16px;text-decoration:none" href="../../index.html" aria-label="Return to Main Hub">Main Hub</a>
  <button class="btn btn-pri" style="height:42px" id="newTask" aria-label="New task">${ico('plus',16,2.2)}<span class="t">New task</span></button>
  <div class="avatar">PA</div>`;
 b.appendChild(t);
 const tick=()=>{const d=new Date();const h=String(d.getHours()).padStart(2,'0'),m=String(d.getMinutes()).padStart(2,'0'),s=String(d.getSeconds()).padStart(2,'0');};tick();
 $('#newTask').onclick=()=>location.href='overview.html#ask';
 J.nav.wheel();J.nav.dock();J.palette();$('#kOpen').onclick=()=>J.palette.open();
 const ins=$('aside.inspector');if(ins)J.inspector(ins);
};
