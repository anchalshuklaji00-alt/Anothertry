from flask import Flask, request, jsonify,Response

app = Flask(__name__)

def max_length(text):
    if len(text) > 420:
        text = text[:420]
    elif len(text) < 420:
        fill_length = 420 - len(text)
        text += "00" * ((fill_length + 1) // 2)
        text = text[:420]
    return text

def generate_packet(id, text):
    msg = text.encode('utf-8').hex()
    txt = max_length(msg)
    packet = f"120000018d08{id}101220022a800308{id}10{id}22d201{txt}28f0ed8db7064a3d0a18efbca2efbcb2efbcb3e385a4efbcadefbcafefbcb2efbcaf10dedd8dae031893b6d3ad0320d7012883f9f7b103420c47524f564553545249544348520261726a520a4c68747470733a2f2f67726170682e66616365626f6f6b2e636f6d2f76392e302f3132303434333431303231333534352f706963747572653f77696474683d313630266865696768743d313630100118017200"
    return packet

@app.route('/Besto-Msg', methods=['GET'])
def Besto():
    id = request.args.get('Id')
    txt = request.args.get('Msg')
    code = request.args.get('Key')

    if not id or not txt or not code:
        return Response(' - Missing Id or Msg or Key !')

    if code != 'C4-BESTO-AK8L':
        return Response(' - Bad / Error Key !')

    packet = generate_packet(id, txt)
    return packet, 200

if __name__ == '__main__':
    app.run(debug=False)
