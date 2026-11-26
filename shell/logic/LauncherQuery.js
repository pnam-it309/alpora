.pragma library

function evaluateConversion(expr) {
    if (!expr) return "";
    const m = expr.trim().match(/^([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z\$€£¥]+)\s*(?:in|to|=|as)\s*([a-zA-Z\$€£¥]+)$/i);
    if (!m) return "";
    const val = parseFloat(m[1]);
    const fromU = m[2].toLowerCase();
    const toU = m[3].toLowerCase();
    if (isNaN(val)) return "";

    // Currency rates (USD base)
    const curRates = {
        usd: 1.0, "$": 1.0,
        eur: 0.92, "€": 0.92,
        gbp: 0.79, "£": 0.79,
        jpy: 152.0, "¥": 152.0,
        vnd: 25400.0,
        cny: 7.23,
        cad: 1.39,
        aud: 1.52
    };
    if (curRates[fromU] !== undefined && curRates[toU] !== undefined) {
        const inUsd = val / curRates[fromU];
        const converted = inUsd * curRates[toU];
        const formatted = converted >= 100 ? converted.toFixed(2) : converted.toFixed(4).replace(/\.?0+$/, "");
        return formatted + " " + toU.toUpperCase();
    }

    // Length
    const lenMeters = {
        km: 1000, m: 1, cm: 0.01, mm: 0.001,
        mi: 1609.344, miles: 1609.344,
        ft: 0.3048, feet: 0.3048,
        in: 0.0254, inch: 0.0254, inches: 0.0254
    };
    if (lenMeters[fromU] !== undefined && lenMeters[toU] !== undefined) {
        const inMeters = val * lenMeters[fromU];
        const converted = inMeters / lenMeters[toU];
        return (Math.abs(converted - Math.round(converted)) < 1e-6 ? Math.round(converted) : converted.toFixed(3).replace(/\.?0+$/, "")) + " " + toU;
    }

    // Mass
    const massKg = {
        kg: 1, g: 0.001, mg: 0.000001,
        lb: 0.45359237, lbs: 0.45359237,
        oz: 0.0283495
    };
    if (massKg[fromU] !== undefined && massKg[toU] !== undefined) {
        const inKg = val * massKg[fromU];
        const converted = inKg / massKg[toU];
        return (Math.abs(converted - Math.round(converted)) < 1e-6 ? Math.round(converted) : converted.toFixed(3).replace(/\.?0+$/, "")) + " " + toU;
    }

    // Temperature
    if ((fromU === "c" || fromU === "celsius") && (toU === "f" || toU === "fahrenheit")) {
        return ((val * 9 / 5) + 32).toFixed(1).replace(/\.0$/, "") + " °F";
    }
    if ((fromU === "f" || fromU === "fahrenheit") && (toU === "c" || toU === "celsius")) {
        return (((val - 32) * 5 / 9)).toFixed(1).replace(/\.0$/, "") + " °C";
    }
    return "";
}

function evaluateMath(expr) {
    if (!expr || expr.length < 2) return "";
    const clean = expr.trim().replace(/\^/g, "**").replace(/\bpi\b/gi, "Math.PI").replace(/\be\b/gi, "Math.E");
    if (!/^[0-9\s\+\-\*\/\%\.\(\)\,\*\*\s]|Math\.(sin|cos|tan|sqrt|pow|abs|round|floor|ceil|log|PI|E)/i.test(clean))
        return "";
    if (!/[\+\-\*\/\%\^]|(sin|cos|tan|sqrt|abs|log)/i.test(expr))
        return "";
    try {
        const fn = new Function("Math", "return (" + clean + ");");
        const res = fn(Math);
        if (typeof res === "number" && isFinite(res)) {
            return Math.abs(res - Math.round(res)) < 1e-9 ? Math.round(res).toString() : res.toFixed(4).replace(/\.?0+$/, "");
        }
    } catch (_) {}
    return "";
}
