/* Personal Agent Orbital · by fls-dev · https://github.com/fls-dev */
/* Personal Agent Orbital — Autonomous Windows Desktop AI Agent Demo & Live Data */
window.JV = window.JV || {};
JV.data = {
  user: { name:'Operator', short:'PA', workspace:'Windows 11', role:'Desktop Controller' },

  /* rooms: order = hotkey 1–9 and the position on the orbit dial. glyph = icon key */
  nav: [
    { id:'overview',     href:'overview.html',     label:'Overview',       short:'Overview',     count:'active', desc:'Host telemetry, active window & GPU standby' },
    { id:'tasks',        href:'tasks.html',        label:'Tasks',          short:'Tasks',        count:'44 tools',desc:'Autonomous plans, element grounding, multi-step actions', live:true },
    { id:'operations',   href:'operations.html',   label:'Desktop Ops',    short:'Desktop',      count:'Win 11', desc:'Mouse, keyboard, UIA trees and active processes' },
    { id:'local-chat',   href:'local-chat.html',   label:'Local chat',     short:'Chat',         count:'qwen3:8b',desc:'Local Ollama reasoning, tool calling & plan-then-act' },
    { id:'fine-tuning',  href:'fine-tuning.html',  label:'Tool Registry',  short:'Tools',        count:'44 safe',desc:'44 validated tools, permission policies & approval gates' },
    { id:'scheduled',    href:'scheduled.html',    label:'Automations',   short:'Automate',     count:'6 jobs', desc:'Desktop workflows, daily routines and cron triggers' },
    { id:'memory',       href:'memory.html',       label:'Agent Memory',   short:'Memory',       count:'SQLite', desc:'Persistent facts, preferences, paths and project state' },
    { id:'integrations', href:'integrations.html', label:'Integrations',   short:'Engines',      count:'6 engines',desc:'Ollama, Windows UIA, PyAutoGUI, File System, SQLite' },
    { id:'audit',        href:'audit.html',        label:'Audit trail',    short:'Audit',        count:'Forensic',desc:'Signed tool execution logs, approval cards & history' }
  ],

  today: { spend:0.00, budget:0.00, ops:42, completed:38, failed:1, running:2, queued:1, models:1, tokens:48210, vsYesterday:+18 },
  trend: [12, 14, 18, 22, 19, 28, 24, 35, 30, 42, 38, 45, 41, 52],

  /* Desktop Subsystem Status */
  fleet: [
    { n:'Windows UI Automation', k:'edge', st:'ok',  v:'UIA Tree Ready', load:.15 },
    { n:'Ollama Engine · Qwen3 8B', k:'llm', st:'ok', v:'GPU Standby', load:.32 },
    { n:'NVIDIA RTX 3050 Laptop', k:'gpu', st:'ok',  v:'6GB VRAM · 14% Load', load:.28 },
    { n:'Intel Core i7-13650HX', k:'cpu',  st:'ok',  v:'14 Cores · 12% CPU', load:.18 },
    { n:'Coordinate Grounding', k:'input', st:'ok',  v:'1920x1080 Calibrated', load:.05 },
    { n:'Safety Permission Guard', k:'safe', st:'ok', v:'Confirmation Armed', load:.02 }
  ],

  /* Personal Agent Desktop Tasks */
  tasks: [
    { id:'T-0104', no:104, t:'Inspect active windows and extract UI controls from Google Chrome', cost:0, st:'run', dur:'running', model:'qwen3:8b · local', time:'21:24', rev:1, tag:'ui_automation',
      steps:[['list_windows',0,1,'done',12],['get_active_window',0,1,'done',8],['inspect_window_elements',0,1,'run',42],['ground_element',0,0,'wait',0]] },
    { id:'T-0103', no:103, t:'Launch Notepad, synthesize release notes, and save file safely', cost:0, st:'run', dur:'running', model:'qwen3:8b · local', time:'21:18', rev:2, tag:'desktop_action',
      steps:[['launch_application',0,1,'done',180],['wait_for_window',0,1,'done',45],['type_text',0,1,'run',120],['write_file_safe',0,0,'wait',0]] },
    { id:'T-0102', no:102, t:'Organize desktop screenshots older than 7 days into Archive folder', cost:0, st:'done', dur:'1.8s', model:'qwen3:8b · local', time:'20:52', rev:1, tag:'file_intelligence',
      steps:[['list_directory',0,1,'done',15],['inspect_file_metadata',0,1,'done',28],['create_directory',0,1,'done',12],['move_file_safe',0,4,'done',85]] },
    { id:'T-0101', no:101, t:'Calibrate mouse cursor and verify coordinate bounds (1920 x 1080)', cost:0, st:'done', dur:'420ms', model:'qwen3:8b · local', time:'20:30', rev:1, tag:'desktop_action',
      steps:[['get_screen_metrics',0,1,'done',5],['move_cursor',0,1,'done',35],['click_coordinate',0,1,'done',18]] },
    { id:'T-0100', no:100, t:'Audit tool permissions and enforce confirmation cards on high-risk actions', cost:0, st:'done', dur:'85ms', model:'qwen3:8b · local', time:'20:05', rev:1, tag:'safety',
      steps:[['check_tool_permission',0,1,'done',8],['validate_arguments',0,1,'done',14],['log_audit_entry',0,1,'done',12]] },
    { id:'T-0099', no:99, t:'Query system processes and verify background GPU VRAM allocation', cost:0, st:'done', dur:'210ms', model:'qwen3:8b · local', time:'19:40', rev:1, tag:'system_control',
      steps:[['list_processes',0,1,'done',24],['get_system_telemetry',0,1,'done',32],['format_report',0,1,'done',10]] },
    { id:'T-0098', no:98, t:'Read project README.md and summarize recent development milestones', cost:0, st:'done', dur:'3.4s', model:'qwen3:8b · local', time:'19:15', rev:1, tag:'file_intelligence',
      steps:[['read_file_safe',0,1,'done',18],['ollama_infer',0,1,'done',3200],['save_memory',0,1,'done',25]] }
  ],

  /* Selected task detail on tasks.html */
  taskDetail: {
    'T-0103': {
      request:'Open Notepad on Windows desktop, type release notes for Milestone C, and save file into workspace with snapshot backup.',
      revisions:[
        { r:1, at:'21:15', note:'Proposed direct shell launch · User confirmation required', cost:0, st:'superseded' },
        { r:2, at:'21:18', note:'Approved · Safe launch through ToolRegistry · 4 steps', cost:0, st:'approved' }
      ],
      plan:[
        { n:1, t:'Launch application "Notepad" via catalog verification', tool:'launch_application', est:0, gate:true },
        { n:2, t:'Wait for window title "Untitled - Notepad" and get HWND', tool:'wait_for_window', est:0, gate:false },
        { n:3, t:'Synthesize text into active text control via physical typing', tool:'type_text', est:0, gate:false },
        { n:4, t:'Create backup snapshot and write to "docs/release_notes.txt"', tool:'write_file_safe', est:0, gate:false }
      ],
      result:'Done: Notepad launched cleanly (PID 18420). Release notes text synthesized (42 words). Backup snapshot saved to data/backups/notes_snap1.txt and verified in 1.4s.',
      files:[
        { n:'release_notes.txt', k:'text/plain', size:'2.4 KB', v:'r1' },
        { n:'execution_audit.json', k:'application/json', size:'4.2 KB', v:'r1' }
      ],
      tokens:{ in:1240, out:380 }
    }
  },

  activity: [
    ['21:24:12','inspect_window_elements','T-0104','Discovered 42 UI controls in foreground window'],
    ['21:23:45','get_active_window','T-0104','Active window: Google Chrome · PID 9412'],
    ['21:18:30','launch_application','T-0103','Notepad launched successfully · HWND 24890'],
    ['20:52:10','move_file_safe','T-0102','Moved 4 screenshot PNGs to Archive folder'],
    ['20:30:15','click_coordinate','T-0101','Hardware mouse click at (960, 540) · primary display'],
    ['20:05:40','validate_arguments','T-0100','Passed Pydantic schema validation · 0 violations'],
    ['19:40:22','get_system_telemetry','T-0099','GPU VRAM: 4218 / 6144 MB · CPU: 12.4%']
  ],
  activityPool: [
    ['ground_element','T-0104','Resolved button "Save As" at BoundingRectangle [840, 620, 920, 650]'],
    ['tokens','T-0104','Ollama response generated at 18.4 tokens/s on RTX 3050'],
    ['safety','T-0103','Confirmation card granted by user for process launch'],
    ['snapshot','T-0102','Snapshot backup created before file write'],
    ['mouse','T-0101','Smooth Bezier cursor movement completed in 180ms']
  ],

  /* local models */
  models: [
    { n:'qwen3:8b (Ollama GPU)', v:48210, c:'#9BE34A' },
    { n:'qwen2.5-coder:7b',     v:14200, c:'#8BE9FF' },
    { n:'llama3.2:3b (Fast)',    v:6400,  c:'#B48CFF' }
  ],

  /* Core Subsystem Connections */
  connections: [
    { id:'ollama',     n:'Ollama Local API · qwen3:8b', s:'Qwen3 8B', k:'Local LLM', cap:1, calls:42, lat:180, spend:0, c:'#9BE34A', url:'http://127.0.0.1:11434' },
    { id:'uia',        n:'Windows UI Automation Engine', s:'UIA Core', k:'Accessibility', cap:14, calls:68, lat:12, spend:0, c:'#8BE9FF' },
    { id:'desktop',    n:'Desktop Mouse & Keyboard Engine', s:'Desktop Input', k:'Hardware Input', cap:8, calls:94, lat:8, spend:0, c:'#FFB36B' },
    { id:'file_intel', n:'Safe File Operations & Sandboxing', s:'File Engine', k:'FileSystem', cap:9, calls:31, lat:4, spend:0, c:'#6CF0C2' },
    { id:'process_mgr',n:'Application & Process Control', s:'Process Mgr', k:'Win32 API', cap:6, calls:18, lat:15, spend:0, c:'#B48CFF' },
    { id:'memory_db',  n:'SQLite Persistent Context Engine', s:'Memory DB', k:'Database', cap:6, calls:54, lat:2, spend:0, c:'#EDEDE6', url:'data/personal_agent.db' }
  ],

  processors: [
    { n:'Safe Windows Workspace Sandbox', ops:'read · write · snapshot · rollback', mime:'text/*, application/json, .py, .bat, .md', limit:'100.0 MB', required:true },
    { n:'Windows Accessibility Tree Inspector', ops:'discover · inspect · extract · ground', mime:'Win32 Controls, WPF, WinUI3, Chromium UIA', limit:'Unrestricted' },
    { n:'Hardware Cursor & Keyboard Synthesizer', ops:'move · click · scroll · type · shortcuts', mime:'Physical HID Simulation', limit:'1920x1080 Bounds Clamped' },
    { n:'Tool Engine & Permission Gate', ops:'validate · check_permission · confirm · audit', mime:'ToolRegistry 44 Tools', limit:'Safe Sandbox' }
  ],

  /* Catalog of 44 Registered Tools */
  catalog: [
    ['list_windows','tools','UI Automation','Discovers all visible top-level desktop windows with handles and processes.',1],
    ['inspect_window_elements','tools','UI Automation','Extracts full UI accessibility tree, controls, and fields.',1],
    ['click_element','tools','UI Automation','Invokes native accessibility click on UI controls without moving physical mouse.',1],
    ['click_coordinate','tools','Desktop Action','Sends hardware mouse click event at exact screen coordinates (X, Y).',1],
    ['type_text','tools','Desktop Action','Synthesizes keyboard input into active focused UI control or desktop location.',1],
    ['move_cursor','tools','Desktop Action','Smoothly moves cursor across screen using human-calibrated Bezier curves.',1],
    ['press_key_combination','tools','Desktop Action','Executes Windows keyboard shortcuts (e.g. Win+D, Ctrl+S).',1],
    ['launch_application','tools','System Control','Executes verified desktop applications from catalog or paths.',1],
    ['terminate_process','tools','Processes','Stops targeted background process safely with user confirmation.',1],
    ['read_file_safe','tools','Files','Safely reads text contents from whitelisted project directory paths.',1],
    ['write_file_safe','tools','Files','Creates or modifies files with automatic backup snapshots and rollback.',1],
    ['get_screen_metrics','tools','System Control','Returns screen resolution, DPI scaling, and monitor layout.',1],
    ['read_clipboard','tools','System Control','Safely reads current Windows clipboard text for agent processing.',1],
    ['qwen3:8b','ai','Local Ollama','Primary local model running on RTX 3050 Laptop GPU (6GB VRAM)',1],
    ['qwen2.5-coder:7b','ai','Local Ollama','Specialized coding model for code analysis and script generation',1],
    ['filesystem','mcp','MCP','Local project files, read and write inside allow-listed workspace.',1],
    ['playwright','mcp','MCP','Browser automation: navigate, inspect DOM, capture screenshots.',1],
    ['sqlite','mcp','MCP','Persistent memory, tool execution history, and audit records.',1]
  ],
  catalogTabs: [ ['all','All Capabilities'], ['tools','Desktop Tools (44)'], ['ai','Local Models'], ['mcp','MCP Bridges'] ],

  /* Tool Safety & Permission Engine */
  ft: {
    base:'ToolRegistry v2.3', method:'Parameter Validation & Permission Tiers', gpu:'NVIDIA RTX 3050 6GB',
    run:{ id:'rule-audit', name:'Safe Execution Policy Armed', status:'active', epoch:44, epochs:44, step:44, steps:44, eta:'Ready', cost:0, lr:'Safe', batch:1, ctx:4096 },
    loss:[0.05, 0.04, 0.03, 0.02, 0.01, 0.01, 0.005, 0.002, 0.001, 0.001],
    evalLoss:[0.06, 0.05, 0.04, 0.03, 0.02, 0.01, 0.008, 0.004, 0.002, 0.001],
    datasets:[
      { n:'Whitelisted Applications', rows:28, tokens:'Catalog', q:100, note:'Chrome, VS Code, Notepad, Terminal, Explorer' },
      { n:'Safe Workspace Roots',     rows:4,  tokens:'Directories', q:100, note:'Project root, docs, logs, data' },
      { n:'Pydantic Parameter Schemas',rows:44, tokens:'Strict JSON', q:100, note:'Strict argument typing and boundary validation' }
    ],
    runs:[
      { id:'perm-01', n:'Confirmation Gate on launch_application', st:'done', loss:0, ev:'100%', cost:0, at:'active' },
      { id:'perm-02', n:'Confirmation Gate on terminate_process',  st:'done', loss:0, ev:'100%', cost:0, at:'active' },
      { id:'perm-03', n:'Auto-permission for read-only tools',     st:'done', loss:0, ev:'100%', cost:0, at:'active' },
      { id:'perm-04', n:'Snapshot Backup on write_file_safe',     st:'done', loss:0, ev:'100%', cost:0, at:'active' }
    ],
    adapters:[ { n:'Emergency Stop Handler', base:'Win32', size:'Native', active:true, score:'100%' }, { n:'Coordinate Boundary Clamping', base:'Win32', size:'Native', active:true, score:'100%' } ]
  },

  /* Local Chat with Qwen3 8B */
  chat: {
    model:'Qwen3 8B (Ollama GPU)', endpoint:'http://127.0.0.1:11434/api/chat', ctx:'8 192', tps:18.4, ttft:120,
    messages:[
      { who:'me', t:'Inspect what applications are open on my computer right now.' },
      { who:'ai', t:'I queried the Windows desktop window hierarchy. You currently have Visual Studio Code, Google Chrome, and Windows Terminal open. Visual Studio Code is currently in the foreground (PID: 14820).', meta:'qwen3:8b · 38 tok · 0.4s · 0 cloud spend' },
      { who:'me', t:'Can you launch Notepad and type the release summary?' },
      { who:'ai', t:'Yes. Launching applications requires user confirmation under our safety policy. Once confirmed, I will launch Notepad, wait for its window, and synthesize the text directly into the editor control.', meta:'qwen3:8b · 44 tok · 0.5s · 0 cloud spend' }
    ],
    presets:['Inspect active window elements','Launch Notepad and type notes','Organize desktop screenshots','Check GPU & CPU hardware usage']
  },

  /* SQLite Persistent Memory */
  memory: {
    total:428, kinds:[['preference',142],['window_cache',98],['file_history',112],['desktop_route',76]],
    items:[
      { k:'preference',   t:'Primary text editor preferred: Visual Studio Code ("Code.exe")', src:'user_config', at:'Today 18:30', w:.95 },
      { k:'desktop_route',t:'Display resolution calibrated: 1920 x 1080 @ 1.0x scale', src:'hardware_probe', at:'Today 14:10', w:.98 },
      { k:'file_history', t:'Project root directory whitelisted: H:\\pro agent', src:'system_init', at:'Today 12:00', w:.99 },
      { k:'window_cache', t:'Chrome window handle cached: HWND 19820, ClassName "Chrome_WidgetWin_1"', src:'list_windows', at:'Today 21:24', w:.88 },
      { k:'preference',   t:'Safety policy: Confirmation card required for destructive operations', src:'security_rule', at:'Today 12:00', w:.99 },
      { k:'desktop_route',t:'Emergency Stop hotkey configured: ESC / Pause break', src:'safety_engine', at:'Today 12:00', w:.95 }
    ]
  },

  /* Automated Desktop Workflows */
  scheduled: [
    { id:'S-01', n:'Morning Desktop Health & RAM Audit', cron:'0 9 * * *',  human:'Daily · 09:00 AM',  next:'in 11 h 35 min', last:'ok', lastAt:'09:00 AM', model:'qwen3:8b · local', cost:0, on:true, h:9 },
    { id:'S-02', n:'Weekly Screenshot Archive Routine',   cron:'0 18 * * 0', human:'Sundays · 18:00',  next:'Sun 18:00',      last:'ok', lastAt:'Sun 18:00', model:'qwen3:8b · local', cost:0, on:true, h:18 },
    { id:'S-03', n:'Idle GPU VRAM & Temperature Monitor',cron:'*/30 * * * *',human:'Every 30 min',    next:'in 6 min',       last:'ok', lastAt:'21:00',     model:'qwen3:8b · local', cost:0, on:true, h:21 },
    { id:'S-04', n:'Workspace Safe Snapshot Backup',     cron:'0 23 * * *', human:'Daily · 23:00',     next:'in 1 h 35 min',  last:'ok', lastAt:'Yesterday', model:'qwen3:8b · local', cost:0, on:true, h:23 }
  ],

  /* Forensic Execution Audit */
  audit: [
    { at:'21:24:12', who:'Personal Agent', act:'uia.inspect', obj:'Chrome_WidgetWin_1 (PID 9412)', sev:'info', ip:'localhost', hash:'8f1a…c2' },
    { at:'21:18:30', who:'User (Card)',   act:'safety.confirm', obj:'launch_application("Notepad")', sev:'warn', ip:'localhost', hash:'4a2e…d9' },
    { at:'20:52:10', who:'Personal Agent', act:'file.move', obj:'4 files → data/archive/', sev:'info', ip:'localhost', hash:'9b3c…71' },
    { at:'20:30:15', who:'Personal Agent', act:'mouse.click', obj:'Coordinate (960, 540) primary', sev:'info', ip:'localhost', hash:'2d4f…88' },
    { at:'20:05:40', who:'Personal Agent', act:'tool.validate', obj:'list_windows(visible_only=True)', sev:'info', ip:'localhost', hash:'5e7b…12' }
  ],

  /* Desktop Control Operations Telemetry */
  ops: {
    throughput:[8, 12, 10, 15, 14, 22, 18, 25, 20, 28, 24, 30, 26, 35, 32, 28, 24, 30, 36, 32, 28, 34, 38, 42],
    queue:[
      { id:'OP-01', task:'T-0104', step:'inspect_window_elements', model:'qwen3:8b · local', st:'run', t:'42 ms', cost:0 },
      { id:'OP-02', task:'T-0103', step:'type_text · release_notes', model:'qwen3:8b · local', st:'run', t:'120 ms', cost:0 },
      { id:'OP-03', task:'T-0104', step:'ground_element', model:'qwen3:8b · local', st:'wait', t:'—', cost:0 }
    ],
    workers:[
      { n:'local · qwen3:8b (Ollama)', load:.32, note:'18.4 tok/s · 4.2 GB VRAM on RTX 3050' },
      { n:'windows · uia_engine',     load:.15, note:'Native accessibility tree walker' },
      { n:'desktop · input_driver',   load:.05, note:'Win32 SendInput coordinate synthesis' },
      { n:'safety · permission_gate', load:.02, note:'Strict argument schema validator' }
    ],
    errors:[ ['terminate_process','User denied confirmation card · System process protected','18:40'] ]
  }
};
