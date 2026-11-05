import React, {useEffect, useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {
  Activity, AlertTriangle, Bell, CloudSun, Database, Droplets, Gauge,
  History, Home, LogOut, MapPinned, Radio, Settings, ShieldCheck,
  Thermometer, Users, Wind, Wrench, RefreshCw, UserCircle, Eye, Server,
  ChevronDown, CheckCircle2, Clock3
} from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';
import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

// Vite no copia automáticamente los iconos Leaflet clásicos en algunos builds.
// Usamos un marcador SVG embebido para que funcione sin assets extra.
const markerIcon = new L.DivIcon({
  className: 'skysense-marker',
  html: '<div class="markerPulse"><div class="markerCore">☁</div></div>',
  iconSize: [42,42], iconAnchor: [21,38], popupAnchor: [0,-36]
});

const ROLE_LABELS = {
  ADMIN: 'Administrador', OPERATOR: 'Operador',
  MAINTENANCE: 'Mantenimiento', VIEWER: 'Consulta'
};

const ROLE_NAV = {
  ADMIN: ['Resumen','Estaciones','Históricos','Alertas','Health','Administración'],
  OPERATOR: ['Resumen','Estaciones','Históricos','Alertas'],
  MAINTENANCE: ['Resumen','Estaciones','Health'],
  VIEWER: ['Resumen','Estaciones','Históricos']
};

const NAV_ICONS = {
  Resumen: Home, Estaciones: Radio, Históricos: History,
  Alertas: Bell, Health: Activity, Administración: Settings
};

const DEMO_USERS = [
  ['Administrador','admin@skysense.co','Admin123!'],
  ['Operador','operador@skysense.co','Operador123!'],
  ['Mantenimiento','mantenimiento@skysense.co','Mantenimiento123!'],
  ['Consulta','consulta@skysense.co','Consulta123!']
];

function App(){
  const [token,setToken] = useState(sessionStorage.getItem('access_token'));
  const [me,setMe] = useState(null);
  const [page,setPage] = useState('Resumen');
  const [stations,setStations] = useState([]);
  const [selected,setSelected] = useState('SKY-001');
  const [latest,setLatest] = useState(null);
  const [history,setHistory] = useState([]);
  const [alerts,setAlerts] = useState([]);
  const [health,setHealth] = useState(null);
  const [users,setUsers] = useState([]);
  const [systemHealth,setSystemHealth] = useState(null);
  const [error,setError] = useState('');
  const [loading,setLoading] = useState(false);

  const headers = useMemo(()=> token ? {Authorization:`Bearer ${token}`} : {},[token]);

  async function request(path, options={}, allowRefresh=true){
    const r=await fetch(API+path,{...options,credentials:'include',headers:{...headers,...(options.headers||{})}});
    if(r.status===401 && allowRefresh && path!=='/auth/refresh'){
      const rr=await fetch(API+'/auth/refresh',{method:'POST',credentials:'include'});
      if(rr.ok){
        const fresh=await rr.json();
        sessionStorage.setItem('access_token',fresh.access_token);
        setToken(fresh.access_token);
        const retryHeaders={...(options.headers||{}),Authorization:`Bearer ${fresh.access_token}`};
        const retry=await fetch(API+path,{...options,credentials:'include',headers:retryHeaders});
        if(retry.ok)return retry.status===204?null:retry.json();
      }
      logout(false); throw new Error('La sesión expiró. Ingresa nuevamente.');
    }
    if(!r.ok){let detail='';try{detail=(await r.json()).detail}catch{};throw new Error(detail||`HTTP ${r.status}`)}
    if(r.status===204)return null;
    return r.json();
  }

  async function loadProfile(){
    if(!token)return;
    try{const profile=await request('/auth/me');setMe(profile);}
    catch(e){setError(e.message)}
  }

  async function refreshAll(code=selected){
    if(!token)return;
    setLoading(true); setError('');
    try{
      const [s,a,sys] = await Promise.all([request('/stations'),request('/alerts'),fetch(API+'/system/health').then(r=>r.json())]);
      const cleanStations=(s||[]).filter(x=>String(x.station_code||'').startsWith('SKY-'));
      setStations(cleanStations); setAlerts(a||[]); setSystemHealth(sys);
      const actualCode=cleanStations.some(x=>x.station_code===code)?code:(cleanStations[0]?.station_code||code);
      setSelected(actualCode);
      const results=await Promise.allSettled([
        request(`/stations/${actualCode}/latest`),
        request(`/stations/${actualCode}/history?limit=48`),
        request(`/stations/${actualCode}/health`)
      ]);
      setLatest(results[0].status==='fulfilled'?results[0].value:null);
      setHistory(results[1].status==='fulfilled'?[...results[1].value].reverse():[]);
      setHealth(results[2].status==='fulfilled'?results[2].value:null);
      if(me?.role==='ADMIN'){
        try{setUsers(await request('/users'))}catch{}
      }
    }catch(e){setError(e.message)}finally{setLoading(false)}
  }

  async function logout(callApi=true){
    if(callApi && token){try{await fetch(API+'/auth/logout',{method:'POST',credentials:'include',headers:{Authorization:`Bearer ${token}`}})}catch{}}
    sessionStorage.removeItem('access_token');setToken(null);setMe(null);setPage('Resumen');
  }

  useEffect(()=>{loadProfile()},[token]);
  useEffect(()=>{if(me)refreshAll(selected)},[me]);
  useEffect(()=>{if(me)refreshAll(selected)},[selected]);

  if(!token) return <Login onLogin={(t)=>{sessionStorage.setItem('access_token',t);setToken(t)}}/>;
  if(!me) return <div className="boot"><CloudSun size={52}/><b>Abriendo SkySense...</b></div>;

  const allowed=ROLE_NAV[me.role]||ROLE_NAV.VIEWER;
  if(!allowed.includes(page)) setTimeout(()=>setPage('Resumen'),0);
  const station=stations.find(s=>s.station_code===selected)||stations[0];
  const activeAlerts=alerts.filter(a=>a.status==='ACTIVE');

  return <div className="appShell">
    <Sidebar role={me.role} allowed={allowed} page={page} setPage={setPage} onLogout={logout}/>
    <main className="content">
      <Topbar me={me} station={selected} stations={stations} setStation={setSelected} loading={loading} onRefresh={()=>refreshAll(selected)} systemHealth={systemHealth}/>
      {error&&<div className="errorBanner">{error}</div>}
      {page==='Resumen'&&<Dashboard station={station} latest={latest} history={history} alerts={alerts} health={health} activeAlerts={activeAlerts} stations={stations}/>} 
      {page==='Estaciones'&&<StationsPage stations={stations} selected={selected} setSelected={(v)=>{setSelected(v);setPage('Resumen')}}/>}
      {page==='Históricos'&&<HistoryPage history={history} station={selected}/>} 
      {page==='Alertas'&&<AlertsPage alerts={alerts} role={me.role} onClose={async id=>{await request(`/alerts/${id}`,{method:'PATCH'});refreshAll(selected)}}/>}
      {page==='Health'&&<HealthPage health={health} systemHealth={systemHealth} station={selected}/>} 
      {page==='Administración'&&me.role==='ADMIN'&&<AdminPage users={users}/>} 
    </main>
  </div>
}

function Login({onLogin}){
  const [email,setEmail]=useState('admin@skysense.co');
  const [password,setPassword]=useState('Admin123!');
  const [show,setShow]=useState(false); const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
  async function submit(e){e.preventDefault();setBusy(true);setError('');try{
    const r=await fetch(API+'/auth/login',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
    if(!r.ok)throw new Error('Usuario o contraseña incorrectos.'); const j=await r.json();onLogin(j.access_token);
  }catch(e){setError(e.message)}finally{setBusy(false)}}
  return <div className="loginPage">
    <div className="loginVisual"><div className="weatherGlow"></div><div className="loginBrand"><CloudSun/><b>SkySense</b><span>Monitoreo meteorológico inteligente</span></div><div className="loginCopy"><span className="eyebrow">SKYSENSE + SKYNODE</span><h1>Información meteorológica clara, segura y oportuna.</h1><p>Telemetría, históricos, alertas y salud técnica de las estaciones desde una única plataforma.</p><div className="loginFeatures"><span><Radio/> Telemetría</span><span><Bell/> Alertas</span><span><ShieldCheck/> Seguridad</span></div></div></div>
    <div className="loginPanel"><form className="loginForm" onSubmit={submit}><div className="mobileBrand"><CloudSun/><b>SkySense</b></div><span className="eyebrow">ACCESO SEGURO</span><h2>Bienvenido</h2><p>Ingresa con tu cuenta de SkySense.</p><label>Correo electrónico<input value={email} onChange={e=>setEmail(e.target.value)} type="email" required/></label><label>Contraseña<div className="passwordField"><input value={password} onChange={e=>setPassword(e.target.value)} type={show?'text':'password'} required/><button type="button" onClick={()=>setShow(!show)}><Eye size={18}/></button></div></label>{error&&<div className="loginError">{error}</div>}<button className="primaryBtn" disabled={busy}>{busy?'Validando...':'Ingresar a SkySense'}</button><div className="demoUsers"><b>Usuarios demo</b>{DEMO_USERS.map(([label,user,pass])=><button type="button" key={user} onClick={()=>{setEmail(user);setPassword(pass)}}><span>{label}</span><small>{user}</small></button>)}</div></form></div>
  </div>
}

function Sidebar({role,allowed,page,setPage,onLogout}){
  return <aside className="sidebar"><div className="logo"><div className="logoIcon"><CloudSun/></div><div><b>SkySense</b><span>Weather Intelligence</span></div></div><nav>{allowed.map(name=>{const Icon=NAV_ICONS[name];return <button key={name} className={page===name?'active':''} onClick={()=>setPage(name)}><Icon size={20}/><span>{name}</span></button>})}</nav><div className="sideFoot"><div className="roleBadge"><ShieldCheck size={18}/><div><small>Perfil actual</small><b>{ROLE_LABELS[role]||role}</b></div></div><button className="logout" onClick={onLogout}><LogOut size={18}/>Cerrar sesión</button></div></aside>
}

function Topbar({me,station,stations,setStation,loading,onRefresh,systemHealth}){
  return <header className="topbar"><div><span className="eyebrow">PLATAFORMA METEOROLÓGICA</span><h1>SkySense Dashboard</h1><p>Monitoreo meteorológico en tiempo real</p></div><div className="topActions"><label className="stationSelect"><Radio size={18}/><span><small>Estación</small><select value={station} onChange={e=>setStation(e.target.value)}>{stations.map(s=><option key={s.id} value={s.station_code}>{s.station_code}</option>)}</select></span><ChevronDown size={16}/></label><button className="refreshBtn" onClick={onRefresh} title="Actualizar"><RefreshCw size={20} className={loading?'spin':''}/></button><div className={`systemPill ${systemHealth?.status==='ok'?'ok':'bad'}`}><span></span>{systemHealth?.status==='ok'?'Sistema operativo':'Revisar sistema'}</div><div className="profile"><UserCircle/><div><b>{me.email.split('@')[0]}</b><span>{ROLE_LABELS[me.role]||me.role}</span></div></div></div></header>
}

function Dashboard({station,latest,history,alerts,health,activeAlerts,stations}){
  const chart=history.map(x=>({...x,label:formatHour(x.timestamp_utc)}));
  const age=latest?Math.round(latest.age_seconds):null;
  return <>
    <section className="kpis five"><Kpi icon={Radio} tone="blue" title="Estaciones activas" value={stations.filter(s=>s.status==='ONLINE').length} note={`de ${stations.length} registradas`}/><Kpi icon={AlertTriangle} tone="orange" title="Alertas activas" value={activeAlerts.length} note={activeAlerts.length?'requieren revisión':'sin novedades'}/><Kpi icon={Activity} tone="cyan" title="Último dato" value={age!=null?`${age} s`:'Sin datos'} note="edad de la telemetría"/><Kpi icon={ShieldCheck} tone="green" title="Calidad" value={latest?.quality||'-'} note="quality flag"/><Kpi icon={CheckCircle2} tone="green" title="Estado health" value={health?'Operativo':'Sin health'} note={health?'último reporte recibido':'pendiente de reporte'}/></section>
    <section className="stationHero panel"><div className="stationHeroTitle"><div><div className="stationIcon"><Radio/></div><div><span className="eyebrow">ESTACIÓN SELECCIONADA</span><h2>{station?.station_code||'SKY-001'} <span className="onlineBadge">● {station?.status||'ONLINE'}</span></h2><p>{station?.name||'Estación meteorológica SkySense'}</p></div></div><div className="weatherScene"><CloudSun/><span>Monitoreo activo</span></div></div><div className="metricGrid"><Metric icon={Thermometer} tone="coral" title="Temperatura" value={latest?.temperature_c} unit="°C"/><Metric icon={Droplets} tone="blue" title="Humedad" value={latest?.humidity_pct} unit="%"/><Metric icon={Gauge} tone="purple" title="Presión" value={latest?.pressure_hpa} unit="hPa"/><Metric icon={Wind} tone="cyan" title="Viento" value={latest?.wind_speed_ms} unit="m/s"/><Metric icon={Wind} tone="blue" title="Dirección" value={latest?.wind_direction_deg} unit="°"/><Metric icon={CloudSun} tone="green" title="Density Altitude" value={latest?.density_altitude_ft} unit="ft"/></div></section>
    <section className="chartsGrid"><ChartPanel title="Temperatura y humedad" subtitle="Últimas lecturas"><ResponsiveContainer width="100%" height={250}><LineChart data={chart}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis yAxisId="left"/><YAxis yAxisId="right" orientation="right"/><Tooltip/><Line yAxisId="left" type="monotone" dataKey="temperature_c" name="Temperatura °C" stroke="#fb6b55" strokeWidth={3} dot={false}/><Line yAxisId="right" type="monotone" dataKey="humidity_pct" name="Humedad %" stroke="#2d8cff" strokeWidth={3} dot={false}/></LineChart></ResponsiveContainer></ChartPanel><ChartPanel title="Velocidad del viento" subtitle="Últimas lecturas"><ResponsiveContainer width="100%" height={250}><BarChart data={chart}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis/><Tooltip/><Bar dataKey="wind_speed_ms" name="Viento m/s" fill="#24c7df" radius={[7,7,0,0]}/></BarChart></ResponsiveContainer></ChartPanel></section>
    <section className="bottomGrid"><AlertsCard alerts={alerts}/><HealthCard health={health}/><MapCard station={station}/></section>
  </>
}

function Kpi({icon:Icon,tone,title,value,note}){return <div className={`kpi ${tone}`}><div className="kpiIcon"><Icon/></div><div><span>{title}</span><b>{value}</b><small>{note}</small></div><div className="wave"></div></div>}
function Metric({icon:Icon,tone,title,value,unit}){return <div className={`metric ${tone}`}><div className="metricIcon"><Icon/></div><span>{title}</span><b>{value??'-'} <small>{unit}</small></b><div className="metricWave"></div></div>}
function ChartPanel({title,subtitle,children}){return <div className="panel chartPanel"><div className="panelHeading"><div><h3>{title}</h3><span>{subtitle}</span></div></div>{children}</div>}
function AlertsCard({alerts}){return <div className="panel alertsCard"><div className="panelHeading"><div><h3><Bell size={20}/> Alertas recientes</h3><span>Eventos detectados por reglas</span></div></div>{alerts.length?alerts.slice(0,4).map(a=><div className={`alertItem ${a.severity?.toLowerCase()}`} key={a.id}><div className="alertIco"><AlertTriangle/></div><div><b>{a.station} · {a.rule}</b><span>{a.severity} · {formatDate(a.started_at)}</span></div><strong>{a.value}</strong></div>):<Empty text="No hay alertas registradas"/>}</div>}
function HealthCard({health}){return <div className="panel healthCard"><div className="panelHeading"><div><h3><Activity size={20}/> Health del sistema</h3><span>Estado técnico de la estación</span></div></div><HealthRow label="API" value="Operativo" ok/><HealthRow label="MQTT" value="Configurado" ok/><HealthRow label="Batería" value={health?.battery_pct!=null?`${health.battery_pct}%`:'Sin dato'} ok={health?.battery_pct==null||health.battery_pct>25}/><HealthRow label="Señal RSSI" value={health?.rssi_dbm!=null?`${health.rssi_dbm} dBm`:'Sin dato'} ok={health?.rssi_dbm==null||health.rssi_dbm>-95}/><HealthRow label="Firmware" value={health?.firmware||'Sin dato'} ok/></div>}
function HealthRow({label,value,ok}){return <div className="healthRow"><span>{label}</span><b className={ok?'good':'warn'}><i></i>{value}</b></div>}
function MapCard({station}){const lat=station?.latitude??4.7110,lon=station?.longitude??-74.0721;return <div className="panel mapCard"><div className="panelHeading"><div><h3><MapPinned size={20}/> Ubicación de la estación</h3><span>OpenStreetMap + Leaflet</span></div></div><div className="mapWrap"><MapContainer key={`${lat}-${lon}`} center={[lat,lon]} zoom={12} scrollWheelZoom={false}><TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/><Marker position={[lat,lon]} icon={markerIcon}><Popup><b>{station?.station_code}</b><br/>{station?.name}<br/>{lat.toFixed(5)}, {lon.toFixed(5)}</Popup></Marker></MapContainer></div></div>}

function StationsPage({stations,selected,setSelected}){return <Page title="Estaciones" subtitle="Inventario y ubicación de nodos SkyNode"><div className="stationsLayout"><div className="panel stationList">{stations.map(s=><button key={s.id} className={s.station_code===selected?'selected':''} onClick={()=>setSelected(s.station_code)}><div className="stationDot"><Radio/></div><div><b>{s.station_code}</b><span>{s.name}</span><small>{s.latitude?.toFixed?.(4)}, {s.longitude?.toFixed?.(4)} · FW {s.firmware||'-'}</small></div><em>{s.status}</em></button>)}</div><div className="panel fullMap"><MapContainer center={[4.67,-74.08]} zoom={11} scrollWheelZoom={true}><TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>{stations.filter(s=>s.latitude&&s.longitude).map(s=><Marker key={s.id} position={[s.latitude,s.longitude]} icon={markerIcon}><Popup><b>{s.station_code}</b><br/>{s.name}<br/>{s.status}</Popup></Marker>)}</MapContainer></div></div></Page>}
function HistoryPage({history,station}){const chart=[...history].map(x=>({...x,label:formatHour(x.timestamp_utc)}));return <Page title="Históricos" subtitle={`Series meteorológicas de ${station}`}><div className="chartsGrid"><ChartPanel title="Temperatura" subtitle="Evolución temporal"><ResponsiveContainer width="100%" height={300}><AreaChart data={chart}><defs><linearGradient id="temp" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#fb6b55" stopOpacity={.35}/><stop offset="95%" stopColor="#fb6b55" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis/><Tooltip/><Area type="monotone" dataKey="temperature_c" stroke="#fb6b55" fill="url(#temp)" strokeWidth={3}/></AreaChart></ResponsiveContainer></ChartPanel><ChartPanel title="Presión atmosférica" subtitle="Evolución temporal"><ResponsiveContainer width="100%" height={300}><LineChart data={chart}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis domain={['dataMin - 2','dataMax + 2']}/><Tooltip/><Line type="monotone" dataKey="pressure_hpa" stroke="#7d66e8" strokeWidth={3} dot={false}/></LineChart></ResponsiveContainer></ChartPanel></div><div className="panel dataTable"><table><thead><tr><th>Fecha</th><th>Temp.</th><th>Humedad</th><th>Presión</th><th>Viento</th><th>Dirección</th><th>Calidad</th></tr></thead><tbody>{[...history].reverse().map((x,i)=><tr key={i}><td>{formatDate(x.timestamp_utc)}</td><td>{x.temperature_c??'-'} °C</td><td>{x.humidity_pct??'-'} %</td><td>{x.pressure_hpa??'-'} hPa</td><td>{x.wind_speed_ms??'-'} m/s</td><td>{x.wind_direction_deg??'-'}°</td><td><span className="qualityBadge">{x.quality}</span></td></tr>)}</tbody></table></div></Page>}
function AlertsPage({alerts,role,onClose}){return <Page title="Alertas" subtitle="Seguimiento de condiciones fuera de umbral"><div className="panel dataTable"><table><thead><tr><th>Estación</th><th>Regla</th><th>Severidad</th><th>Valor</th><th>Inicio</th><th>Estado</th><th></th></tr></thead><tbody>{alerts.map(a=><tr key={a.id}><td><b>{a.station}</b></td><td>{a.rule}</td><td><span className={`severity ${a.severity?.toLowerCase()}`}>{a.severity}</span></td><td>{a.value}</td><td>{formatDate(a.started_at)}</td><td>{a.status}</td><td>{a.status==='ACTIVE'&&['ADMIN','OPERATOR'].includes(role)&&<button className="smallBtn" onClick={()=>onClose(a.id)}>Cerrar</button>}</td></tr>)}</tbody></table>{!alerts.length&&<Empty text="No hay alertas"/>}</div></Page>}
function HealthPage({health,systemHealth,station}){return <Page title="Health" subtitle={`Estado técnico de ${station}`}><section className="kpis"><Kpi icon={Server} tone="green" title="API" value={systemHealth?.status==='ok'?'Operativa':'Sin respuesta'} note="health check"/><Kpi icon={Database} tone="blue" title="Firmware" value={health?.firmware||'-'} note="versión del SkyNode"/><Kpi icon={Activity} tone="cyan" title="Batería" value={health?.battery_pct!=null?`${health.battery_pct}%`:'-'} note="último reporte"/><Kpi icon={Radio} tone="purple" title="RSSI" value={health?.rssi_dbm!=null?`${health.rssi_dbm} dBm`:'-'} note="nivel de señal"/></section><div className="panel healthDetail"><h3>Detalle de salud</h3><div className="healthCards"><HealthDetail icon={Clock3} title="Uptime" value={health?.uptime_s!=null?formatDuration(health.uptime_s):'Sin dato'}/><HealthDetail icon={Activity} title="Memoria" value={health?.memory_pct!=null?`${health.memory_pct}%`:'Sin dato'}/><HealthDetail icon={RefreshCw} title="Reinicios" value={health?.reboots??'Sin dato'}/><HealthDetail icon={Clock3} title="Último health" value={health?.timestamp_utc?formatDate(health.timestamp_utc):'Sin dato'}/></div></div></Page>}
function HealthDetail({icon:Icon,title,value}){return <div><Icon/><span>{title}</span><b>{value}</b></div>}
function AdminPage({users}){return <Page title="Administración" subtitle="Usuarios y roles de acceso"><div className="adminCards"><div className="panel"><div className="panelHeading"><div><h3><Users size={20}/> Usuarios registrados</h3><span>RBAC aplicado por perfil</span></div></div><div className="userGrid">{users.map(u=><div className="userCard" key={u.id}><UserCircle/><div><b>{u.email}</b><span>{ROLE_LABELS[u.role]||u.role}</span></div><em>{u.status}</em></div>)}</div></div><div className="panel rolesPanel"><h3><ShieldCheck size={20}/> Matriz de acceso</h3><RoleLine role="Administrador" items="Todos los módulos, usuarios, reglas y configuración"/><RoleLine role="Operador" items="Resumen, estaciones, históricos y alertas"/><RoleLine role="Mantenimiento" items="Resumen, estaciones y health"/><RoleLine role="Consulta" items="Resumen, estaciones e históricos"/></div></div></Page>}
function RoleLine({role,items}){return <div className="roleLine"><b>{role}</b><span>{items}</span></div>}
function Page({title,subtitle,children}){return <><div className="pageTitle"><h2>{title}</h2><p>{subtitle}</p></div>{children}</>}
function Empty({text}){return <div className="empty"><CloudSun/><b>{text}</b><span>La información aparecerá aquí cuando esté disponible.</span></div>}
function formatHour(v){try{return new Date(v).toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'})}catch{return ''}}
function formatDate(v){try{return new Date(v).toLocaleString('es-CO')}catch{return v||'-'}}
function formatDuration(sec){const h=Math.floor(sec/3600),m=Math.floor((sec%3600)/60);return `${h} h ${m} min`}

createRoot(document.getElementById('root')).render(<App/>);
