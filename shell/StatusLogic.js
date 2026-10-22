// Pure presentation rules; services supply observed state, never optimistic state.
function network(data) {
    const wifi = wifiStatus(data);
    if (data.wiredConnected) return {kind: "wired", level: 3, busy: false,
        warning: limited(data.connectivity), label: "Ethernet · " + internet(data.connectivity)};
    return wifi;
}
function limited(connectivity) { return ["None", "Limited", "Portal"].includes(connectivity); }
function internet(connectivity) {
    return ({Full: "Есть интернет", None: "Без интернета", Limited: "Ограниченный доступ",
        Portal: "Нужен вход в сеть", Unknown: "Доступ к интернету не проверен"})[connectivity] || "Доступ к интернету не проверен";
}
function wifiLevel(value) {
    const strength = Math.max(0, Math.min(1, Number(value) || 0));
    return strength >= .67 ? 3 : strength >= .34 ? 2 : strength > .05 ? 1 : 0;
}
function wifiStatus(data) {
    if (!data.wifiAvailable) return {kind: "wifi-unavailable", level: 0, busy: false, warning: false, label: "Wi‑Fi недоступен"};
    if (!data.hardwareEnabled) return {kind: "wifi-off", level: 0, busy: false, warning: false, label: "Wi‑Fi заблокирован аппаратно"};
    if (!data.wifiEnabled) return {kind: "wifi-off", level: 0, busy: false, warning: false, label: "Wi‑Fi выключен"};
    if (data.connecting) return {kind: "wifi-connecting", level: 0, busy: true, warning: false, label: "Wi‑Fi · Подключение…"};
    if (!data.connected) return {kind: "wifi-disconnected", level: 0, busy: false, warning: false, label: "Wi‑Fi · Нет подключения"};
    const strength = Math.max(0, Math.min(1, Number(data.strength) || 0));
    return {kind: "wifi", level: wifiLevel(strength),
        busy: false, warning: limited(data.connectivity),
        label: (data.name || "Wi‑Fi") + " · " + Math.round(strength * 100) + "% · " + internet(data.connectivity)};
}
function audio(available, muted, volume) {
    const percent = Math.max(0, Math.round((Number(volume) || 0) * 100));
    return {kind: !available ? "audio-unavailable" : muted || percent === 0 ? "muted" : "volume",
        level: !available || muted || percent === 0 ? 0 : percent < 35 ? 1 : percent < 70 ? 2 : 3,
        label: !available ? "Звук · Нет устройства вывода" : muted ? "Звук выключен · " + percent + "%" : "Громкость · " + percent + "%"};
}
