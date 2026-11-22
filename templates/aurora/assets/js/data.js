/* Personal Agent Aurora · by fls-dev · https://github.com/fls-dev */
/* Personal Agent Aurora — Autonomous Windows Desktop AI Agent Demo & Live Data */
const DATA={
 user:'Operator',
 spend:'0.00', ops:42, completed:38, failed:1, running:2,
 tasks:[
  {id:'T-0104',t:'Inspect active windows and extract UI controls from Google Chrome',cost:'0',st:'run',dur:'running',model:'qwen3:8b · local',steps:[['list_windows',0,1],['get_active_window',0,1],['inspect_window_elements',0,1]],time:'21:24'},
  {id:'T-0103',t:'Launch Notepad, synthesize release notes, and save file safely',cost:'0',st:'run',dur:'running',model:'qwen3:8b · local',steps:[['launch_application',0,1],['type_text',0,1],['write_file_safe',0,1]],time:'21:18'},
  {id:'T-0102',t:'Organize desktop screenshots older than 7 days into Archive folder',cost:'0',st:'done',dur:'1.8s',model:'qwen3:8b · local',steps:[['list_directory',0,1],['inspect_file_metadata',0,1],['move_file_safe',0,1]],time:'20:52'},
  {id:'T-0101',t:'Calibrate mouse cursor and verify coordinate bounds (1920 x 1080)',cost:'0',st:'done',dur:'420ms',model:'qwen3:8b · local',steps:[['get_screen_metrics',0,1],['click_coordinate',0,1]],time:'20:30'},
  {id:'T-0100',t:'Audit tool permissions and enforce confirmation cards on high-risk actions',cost:'0',st:'done',dur:'85ms',model:'qwen3:8b · local',steps:[['check_tool_permission',0,1],['validate_arguments',0,1]],time:'20:05'},
  {id:'T-0099',t:'Query system processes and verify background GPU VRAM allocation',cost:'0',st:'done',dur:'210ms',model:'qwen3:8b · local',steps:[['list_processes',0,1],['get_system_telemetry',0,1]],time:'19:40'}
 ],
 trend:[12, 14, 18, 22, 19, 28, 24, 35, 30, 42, 38, 45, 41, 52],
 activity:[
  ['21:24:12','inspect_window_elements','T-0104','Discovered 42 UI controls in Chrome window'],
  ['21:23:45','get_active_window','T-0104','Foreground: Google Chrome · PID 9412'],
  ['21:18:30','launch_application','T-0103','Notepad launched successfully · HWND 24890'],
  ['20:52:10','move_file_safe','T-0102','Moved 4 screenshot PNGs to Archive folder'],
  ['20:30:15','click_coordinate','T-0101','Hardware mouse click at (960, 540)'],
  ['20:05:40','validate_arguments','T-0100','Passed Pydantic schema validation · 0 violations'],
  ['19:40:22','get_system_telemetry','T-0099','GPU VRAM: 4218 / 6144 MB · CPU: 12.4%']
 ],
 nav:[['Overview','overview'],['Tasks','tasks'],['Operations','ops'],['Local chat','chat'],['Tool Registry','ft'],['Automations','sched'],['Memory','memory'],['Integrations','integrations'],['Audit trail','audit']],
 connections:[
  {n:'Ollama Engine · Qwen3 8B',s:'Qwen3 8B',k:'Local LLM',cap:1,g:'local',calls:42,lat:180,spend:'0',c:'#9BE34A'},
  {n:'Windows UI Automation',s:'UIA Core',k:'Accessibility',cap:14,g:'system',calls:68,lat:12,spend:'0',c:'#8BE9FF'},
  {n:'Desktop Input Synthesizer',s:'Mouse/KB',k:'Hardware Input',cap:8,g:'hardware',calls:94,lat:8,spend:'0',c:'#FFB36B'},
  {n:'Safe File Intelligence',s:'File Engine',k:'FileSystem',cap:9,g:'storage',calls:31,lat:4,spend:'0',c:'#6CF0C2'},
  {n:'Process & App Manager',s:'Process Mgr',k:'Win32 API',cap:6,g:'system',calls:18,lat:15,spend:'0',c:'#B48CFF'},
  {n:'SQLite Persistent Context',s:'Memory DB',k:'Database',cap:6,g:'storage',calls:54,lat:2,spend:'0',c:'#EDEDE6'}
 ],
 processors:[['Windows Workspace Sandbox','text/*, json, py, bat, md','required'],['Accessibility Tree Walker','Win32, WPF, WinUI3, Chromium'],['Hardware Input Synthesizer','Physical Mouse & Keyboard'],['Tool Permission Gate','44 Safe Registered Tools']],
 catalog:[
  ['list_windows','tools','Discovers all visible top-level desktop windows',1],['inspect_window_elements','tools','Extracts full UI accessibility tree',1],['click_element','tools','Invokes native accessibility click on UI controls',1],
  ['click_coordinate','tools','Sends mouse click at exact screen coordinates (X, Y)',1],['type_text','tools','Synthesizes keyboard input into active UI control',1],['move_cursor','tools','Smooth Bezier cursor movement',1],
  ['launch_application','tools','Executes verified desktop applications',1],['terminate_process','tools','Stops background process with confirmation',1],['read_file_safe','tools','Safely reads text contents from workspace',1],
  ['write_file_safe','tools','Creates/edits files with backup snapshot rollback',1],['qwen3:8b','ai','Primary local model on NVIDIA RTX 3050 (6GB VRAM)',1],['qwen2.5-coder:7b','ai','Local coding model for script generation',1]
 ]
};
/* page routing used by the wheel, dock, radial menu and ⌘K */
DATA.pages={overview:'overview.html',tasks:'tasks.html',ops:'operations.html',chat:'local-chat.html',ft:'fine-tuning.html',sched:'scheduled.html',memory:'memory.html',integrations:'integrations.html',audit:'audit.html'};
DATA.dock=['overview','tasks','chat','integrations'];

/* Desktop Control Operations Telemetry */
DATA.ops={
 throughput:[8, 12, 10, 15, 14, 22, 18, 25, 20, 28, 24, 30, 26, 35, 32, 28, 24, 30, 36, 32, 28, 34, 38, 42],
 fails:[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 queue:[
  ['OP-01','inspect_window_elements','T-0104','qwen3:8b · local','run','42ms',0],
  ['OP-02','type_text · release_notes','T-0103','qwen3:8b · local','run','120ms',0],
  ['OP-03','ground_element','T-0104','qwen3:8b · local','wait','—',0]
 ],
 workers:[
  ['local · qwen3:8b (Ollama)',.32,'18.4 tok/s · 4.2 GB VRAM on RTX 3050'],
  ['windows · uia_engine',.15,'Native accessibility tree walker'],
  ['desktop · input_driver',.05,'Win32 SendInput coordinate synthesis'],
  ['safety · permission_gate',.02,'Strict argument schema validator']
 ],
 errors:[['terminate_process','User denied confirmation card · System process protected','18:40']]
};
