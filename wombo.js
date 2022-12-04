// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: cyan; icon-glyph: magic;
async function identif(key) {
	let req = new Request("https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + key);
	req.method = "post";
	req.body = JSON.stringify({
		"key": key
	});
	let res = await req.loadJSON();
	res.idToken
	return res.idToken;
}

async function timeout(delay) {
	var before = Date.now();
	while (Date.now() < before + delay) { };
	return true;
}


async function create(prompt, style, idToken,task_id=null) {
	let req = new Request("https://paint.api.wombo.ai/api/tasks", data = '{"premium": false}');
	req.method = "post";
	let headers = {
		"Authorization": "bearer " + idToken,
		"Origin": "https://paint.api.wombo.ai/",
		"Referer": "https://paint.api.wombo.ai/",
		"User-Agent": "Mozilla/5.0",
	};
	req.headers = headers;
	body = '{"input_spec":{"prompt":"' + prompt + '","style":' + style + ',"display_freq":10}}';
	req.body = body;
	let res = await req.loadJSON();
	task_id = res.id;

	let task_status_url = "https://paint.api.wombo.ai/api/tasks/" + task_id;
	req = new Request(task_status_url, data = body);
	req.method = "put";
	req.headers = headers;
	req.body = body;
	latest_task = await req.loadJSON();
	req.method = "get";
	req.body = "";
	latest_task = await req.loadJSON();
	repeat_count = 1;
	while (latest_task.state != "completed") {
//		console.log(latest_task);
		await timeout(1000);
		latest_task = await req.loadJSON();
		if (repeat_count > 10){
			log("time out");
			return ("Time out.");
		}
		repeat_count++;
	}
	req = new Request("https://paint.api.wombo.ai/api/tradingcard/" + task_id);
	req.headers = headers;	
	req.method = "post";
	let img_url = await req.loadString();
	return img_url;
}

async function download_img(img_url,fm,path){
  let req=new Request(img_url);
  let res = await req.load();
  fm.write(path,res);
}

let fm = FileManager.iCloud();
let dirPath = fm.documentsDirectory();

let w1_path = fm.joinPath(dirPath, "wombo/words1.txt");
await fm.downloadFileFromiCloud(w1_path)
let words1 = fm.readString(w1_path);

let w2_path = fm.joinPath(dirPath, "wombo/words2.txt");
await fm.downloadFileFromiCloud(w2_path)
let words2 = fm.readString(w2_path);

let styles_path = fm.joinPath(dirPath, "wombo/styles.txt");
await fm.downloadFileFromiCloud(styles_path)
let styles = fm.readString(styles_path);


let prompt = args.shortcutParameter;
prompt = "dog in dust";
let style = "68";
let idToken = await identif("AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw");
let img_url = await create(prompt, style, idToken);
//let img_url="https://images.wombo.art/exports/fc3a3d23-9e1f-4dbd-bafa-36f17ed63256/blank_tradingcard.jpg?Expires=1677351988&Signature=MabwBYsyBZMugJzRULcAP4mBLn5yyI5aZ5NStHT4kp53wS2laB~XYhtGdv87M0RobxAxyBc~FwFr1HuUtIhKRhBX66l8IYjl7x8y3ZFkcgssIoFhgBkWX-0YNKWJCO48XGeC5Mmhojrd8zhXKikvY1vRjSbp6gYxOXzURHh2dZWPSYmL3GB~2asw2V4vpuVHqgpE9NAb5Se7MdIRbLjpWgwIW48QBhcJ5QnihueQIEP~jtJ0WK9AWMyl-Ub5RIkJx9c2XjcpURARxuu1pgMNnp8rcEssaM0bqEk8knSo6u8FZFGDXdVOuThxNvJxOC4U~cW7Gy1FKG5AXq5w0U7hAg__&Key-Pair-Id=K1ZXCNMC55M2IL";
img_url=img_url.replaceAll('"','');
//console.log(prompt);
//console.log(img_url);
await download_img(img_url,fm,fm.joinPath(dirPath, "wombo/res.jpg"));
log(prompt)


