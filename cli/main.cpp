#include <iostream>
#include <cstdlib>
#include <sys/stat.h>
#include <vector>
#include <string>

#ifdef _WIN32
#include <windows.h>
#include <shlwapi.h>
#pragma comment(lib, "shlwapi.lib")
#else
#include <unistd.h>
#endif

using namespace std;

vector<string> proxies = {
    "https://",  // 原始地址最后尝试
    "https://ghfast.top/",
};

const string base_url = "github.com/ncatbot/NcatBot-Plugins/releases/download/v1.0.0/package.zip";
const string target_dir = "ncatbot";

bool file_exists(const string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}

bool download_win(const string& url) {
    cout << "Trying download via: " << url << endl;

    // 尝试多种下载方式
    const vector<string> cmds = {
        "powershell -Command \"Invoke-WebRequest -Uri '" + url + "' -OutFile 'package.zip'\"",
    };

    for (const auto& cmd : cmds) {
        if (system(cmd.c_str()) == 0 && file_exists("package.zip")) {
            return true;
        }
        system("del package.zip 2>nul");
    }
    return false;
}

bool download_linux(const string& url) {
    cout << "Trying download via: " << url << endl;

    const vector<string> cmds = {
        "wget -O package.zip \"" + url + "\"",
        "curl -L -o package.zip \"" + url + "\""
    };

    for (const auto& cmd : cmds) {
        if (system(cmd.c_str()) == 0 && file_exists("package.zip")) {
            return true;
        }
        system("rm -f package.zip");
    }
    return false;
}

bool download() {
    for (const auto& proxy : proxies) {
        string url = proxy + base_url;
#ifdef _WIN32
        if (download_win(url)) return true;
#else
        if (download_linux(url)) return true;
#endif
    }
    return false;
}

bool extract() {
    std::cerr << "解压中...";
    system(("rm -rf " + target_dir).c_str());
    mkdir(target_dir.c_str());

#ifdef _WIN32
    if (system("powershell -Command \"Expand-Archive -Path package.zip -DestinationPath ncatbot\"") != 0)
        return false;
#else
    if (system("unzip -q package.zip -d ncatbot") != 0)
        return false;
#endif

    // 重命名package->Python
    if (rename((target_dir + "/package").c_str(), (target_dir + "/Python").c_str()) != 0) {
        perror("Rename failed");
        return false;
    }

    return true;
}

void setup_env() {
    string python_path = target_dir + "/Python";

#ifdef _WIN32
    python_path += "/python.exe";
    string cmd = "\"" + python_path + "\" -m pip install ncatbot";
#else
    python_path += "/bin/python3";
    string cmd = python_path + " -m pip install ncatbot";
#endif

    system(cmd.c_str());
    cmd = python_path + " -m ncatbot.cli.main";
    system(cmd.c_str());
}

int main() {
    if (!download()) {
        cerr << "All download attempts failed!" << endl;
        return 1;
    }

    if (!extract()) {
        cerr << "Extraction failed!" << endl;
        return 1;
    }

    setup_env();
    return 0;
}
