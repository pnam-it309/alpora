.pragma library

function size(kind) {
    return kind === "clock" ? {width: 460, height: 200}
        : kind === "weather" ? {width: 370, height: 200}
        : kind === "music" ? {width: 370, height: 190}
        : kind === "developer" ? {width: 410, height: 206}
        : {width: 390, height: 360};
}

function bounds(kind, setting, width, height, top) {
    return boundsForSize(setting, width, height, top, size(kind));
}

function boundsForSize(setting, width, height, top, natural) {
    const s = setting || {x: 50, y: 50};
    const scale = Math.max(0.25, Math.min(1, width / 1000, height / 800));
    const margin = 20 * scale;
    const w = Math.min(natural.width * scale, Math.max(1, width - margin * 2));
    const h = Math.min(natural.height * scale, Math.max(1, height - top - margin));
    const origin = Math.min(top, Math.max(0, height - h - margin));
    return {x: margin + Math.max(0, width - margin * 2 - w) * (typeof s.x === "number" ? s.x : 50) / 100,
        y: origin + Math.max(0, Math.min((typeof s.y === "number" ? s.y : 50) * scale, height - origin - margin - h)),
        width: w, height: h, scale: scale, margin: margin, top: origin};
}

function position(kind, setting, x, y, width, height, top) {
    const b = bounds(kind, setting, width, height, top);
    const free = width - b.margin * 2 - b.width;
    return {x: Math.round(Math.max(0, Math.min(100, free > 0 ? (x - b.margin) / free * 100 : 0))),
        y: Math.round(Math.max(0, Math.min(height - b.top - b.margin - b.height, y - b.top)) / b.scale)};
}
