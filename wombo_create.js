async function sign_up(key) {
    // body = { "key": key }
    let req = new Request("https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + key);
    req.method = "post";
    req.body = {
        "key": key
    }
    // req.headers = {
    //     "x-something": "foo bar",
    //     "Content-Type": "application/json"
    // };
    try {

        let res = await req.loadJSON();
        log(JSON.stringify(res, null, 2));
    }
    catch (err) {
        console.log(err);
    }

    return res;

    // if r.status_code != requests.codes.ok:
    //     error = f"Error during identification. Status code error: {r.status_code}"
    // print(error)
    // assert False, error

    // if DEBUG:
    //     print("Google identification sign up.")
    // id_token = r.json()["idToken"]
    // if DEBUG:
    //     print("  => idToken got.")
    // return id_token

}


key = "AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw";


async function main() {
    const asyncMsg = Promise.resolve(sign_up(key));
    console.log(asyncMsg);
}


main();

