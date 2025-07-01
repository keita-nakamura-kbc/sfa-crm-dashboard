// Microsoft Edge用のポリフィル
// Loading画面で止まる問題を解決

// Promise.allSettled polyfill for older Edge versions
if (!Promise.allSettled) {
    Promise.allSettled = function(promises) {
        return Promise.all(promises.map(p => Promise.resolve(p).then(
            value => ({
                status: 'fulfilled',
                value: value,
            }),
            error => ({
                status: 'rejected',
                reason: error,
            })
        )));
    };
}

// Object.fromEntries polyfill
if (!Object.fromEntries) {
    Object.fromEntries = function(entries) {
        if (!entries || !entries[Symbol.iterator]) {
            throw new Error('Object.fromEntries() requires an iterable argument');
        }
        
        const obj = {};
        
        for (const [key, value] of entries) {
            obj[key] = value;
        }
        
        return obj;
    };
}

// Array.prototype.flat polyfill
if (!Array.prototype.flat) {
    Array.prototype.flat = function(depth = 1) {
        return depth > 0 ? 
            this.reduce((acc, val) => acc.concat(
                Array.isArray(val) ? val.flat(depth - 1) : val
            ), [])
            : this.slice();
    };
}

// Edge specific console message
if (navigator.userAgent.indexOf('Edg') > -1) {
    console.log('Edge browser detected - polyfills loaded');
}