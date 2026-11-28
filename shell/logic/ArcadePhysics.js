.pragma library

// Standard physics constants for ALPORA Desktop Arcade Engine
const GRAVITY = 0.44;
const FRICTION = 0.995;
const RESTITUTION = 0.78;
const MAX_VELOCITY = 28.0;
const SLING_MULTIPLIER = 0.18;
const COMPANION_CATCH_RADIUS = 58.0;
const FLOOR_STOP_THRESHOLD = 2.0;

function createBallState(x, y) {
    return {
        x: x || 0,
        y: y || 0,
        vx: 4.5,
        vy: -2.0,
        radius: 18.0
    };
}

function calculateThrowVelocity(pullX, pullY) {
    return {
        vx: Math.max(-MAX_VELOCITY, Math.min(MAX_VELOCITY, pullX * SLING_MULTIPLIER)),
        vy: Math.max(-MAX_VELOCITY, Math.min(MAX_VELOCITY, pullY * SLING_MULTIPLIER))
    };
}

function calculatePointVelocity(dx, dy, speed) {
    const s = speed || 18.0;
    const len = Math.max(1.0, Math.hypot(dx, dy));
    return {
        vx: (dx / len) * s,
        vy: Math.min(-6.0, (dy / len) * s)
    };
}
