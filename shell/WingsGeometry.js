.pragma library

// Shape-preserving cubic Hermite interpolation, matching study 03 in Motion Lab.
// Prepare coefficients only when the final panel or source button changes.
function prepare(source, width, height) {
    const center = Math.max(24, Math.min(width - 24, source.x + source.width / 2));
    const times = [0, 0.34, 0.84, 1];
    const points = [
        [source.x, source.y, Math.max(1, source.width), Math.max(1, source.height)],
        [center - 15, 0, 30, height],
        [0, 0, width, height],
        [0, 0, width, height]
    ];
    const result = [];
    for (let key = 0; key < 4; key++) {
        const rates = [], slopes = [];
        for (let j = 0; j < 3; j++)
            rates.push((points[j + 1][key] - points[j][key]) / (times[j + 1] - times[j]));
        slopes.push(rates[0]);
        for (let j = 1; j < 3; j++) {
            const a = rates[j - 1], b = rates[j];
            const h0 = times[j] - times[j - 1], h1 = times[j + 1] - times[j];
            slopes.push(a * b <= 0 ? 0 : 3 * (h0 + h1) / ((2 * h1 + h0) / a + (h1 + 2 * h0) / b));
        }
        slopes.push(rates[2]);
        result.push({ points: points.map(p => p[key]), slopes: slopes });
    }
    return result;
}

function smooth(value) {
    const t = Math.max(0, Math.min(1, value));
    return t * t * t * (10 + t * (-15 + 6 * t));
}

function coordinate(path, progress, key) {
    const u = smooth(progress), times = [0, 0.34, 0.84, 1];
    const j = u <= 0.34 ? 0 : u <= 0.84 ? 1 : 2;
    const h = times[j + 1] - times[j], t = (u - times[j]) / h;
    const t2 = t * t, t3 = t2 * t, axis = path[key];
    return (2 * t3 - 3 * t2 + 1) * axis.points[j]
        + (t3 - 2 * t2 + t) * h * axis.slopes[j]
        + (-2 * t3 + 3 * t2) * axis.points[j + 1]
        + (t3 - t2) * h * axis.slopes[j + 1];
}
