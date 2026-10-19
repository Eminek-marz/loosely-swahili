import urllib.request
import json

# 1. Test Code Execution
req1 = urllib.request.Request(
    'http://127.0.0.1:7860/api/exec/run',
    data=json.dumps({'code': 'print("ANJIRU_EXEC_SUCCESS", 42 * 2)', 'language': 'python'}).encode(),
    headers={'Content-Type': 'application/json'}
)
r1 = json.loads(urllib.request.urlopen(req1).read().decode())
print('EXEC RESULT:', r1['status'], '| STDOUT:', r1['stdout'].strip(), '| DURATION:', r1['duration_ms'], 'ms')

# 2. Test File Explorer
req2 = urllib.request.Request('http://127.0.0.1:7860/api/workspace/files')
r2 = json.loads(urllib.request.urlopen(req2).read().decode())
print('WORKSPACE FILES FOUND:', len(r2['files']), '| FIRST 3:', [f['path'] for f in r2['files'][:3]])

# 3. Test File Read
req3 = urllib.request.Request(
    'http://127.0.0.1:7860/api/workspace/read',
    data=json.dumps({'path': 'app.py'}).encode(),
    headers={'Content-Type': 'application/json'}
)
r3 = json.loads(urllib.request.urlopen(req3).read().decode())
print('READ app.py:', r3['status'], '| SIZE:', r3['size'], 'bytes')

# 4. Test Auto-Debug Diagnosis
req4 = urllib.request.Request(
    'http://127.0.0.1:7860/api/debug/diagnose',
    data=json.dumps({
        'code': 'items = [1, 2]\nprint(items[10])',
        'traceback': 'IndexError: list index out of range at line 2',
        'language': 'sheng'
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
r4 = json.loads(urllib.request.urlopen(req4).read().decode())
print('AUTO-DEBUG DIAGNOSIS:', r4['status'], '| MESSAGE:', r4['diagnosis'][:65], '...')
