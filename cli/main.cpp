// build this
/*
prerequisite:
- mingw64
- package.zip in repo root
- minizip && zlib installed

1. build package.zip to package.o:
windres cli/resource.rc resource.o

2. static compile with mingw64:
g++ -o main.exe cli/main.cpp resource.o -I "path/to/minizip/include" -I "path/to/zlib/include" -L "path/to/minizip/lib" -L "path/to/zlib/lib" -lminizip -lzlibstatic -fpermissive --static

g++ -o main.exe cli/main.cpp resource.o -I "C:\Users\huany\Desktop\work_space\ziptools-install\minizip-install\include" -I "C:\Users\huany\Desktop\work_space\ziptools-install\zlib-install\include" -L "C:\Users\huany\Desktop\work_space\ziptools-install\minizip-install\lib\" -L "C:\Users\huany\Desktop\work_space\ziptools-install\zlib-install\lib\" -lminizip -lzlibstatic -fpermissive --static



*/
#include <filesystem>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <sys/stat.h>
#include <vector>
#include <string>
#include <fstream>
#include <unzip.h>
#include <iowin32.h>

#ifdef _WIN32
#include <windows.h>
#include <shlwapi.h>
#pragma comment(lib, "shlwapi.lib")
#else
#include <unistd.h>
#endif

using namespace std;

const string TMP_ZIP_FILE = ".temp.zipfile.zip";

vector<string> proxies = {
    "https://ghfast.top/",
    "https://",  // 原始地址最后尝试
};

const string base_url = "github.com/ncatbot/NcatBot-Plugins/releases/download/v1.0.0/package.zip";
const string target_dir = "ncatbot";

bool file_exists(const string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}

#ifdef _WIN32
bool LoadEmbeddedZip(const char* resourceName, std::vector<unsigned char>& data) {
    HRSRC hResource = FindResource(NULL, resourceName, RT_RCDATA);
    if (!hResource) {
        std::cerr << "Failed to find resource." << std::endl;
        return false;
    }

    HGLOBAL hLoadedResource = LoadResource(NULL, hResource);
    if (!hLoadedResource) {
        std::cerr << "Failed to load resource." << std::endl;
        return false;
    }

    void* pResourceData = LockResource(hLoadedResource);
    DWORD dataSize = SizeofResource(NULL, hResource);

    data.resize(dataSize);
    memcpy(data.data(), pResourceData, dataSize);

    return true;
}


bool extractZipFile(const std::string& zipFilePath, const std::string& outputDir) {
    cerr << "解压中..." << std::endl;
    unzFile zipFile = unzOpen(zipFilePath.c_str());
    if (!zipFile) {
        std::cerr << "Failed to open zip file: " << zipFilePath << std::endl;
        return false;
    }

    // Ensure the output directory exists
    if (!std::filesystem::exists(outputDir)) {
        std::filesystem::create_directories(outputDir);
    }

    int err = unzGoToFirstFile(zipFile);
    while (err == UNZ_OK) {
        unz_file_info fileInfo;
        char fileName[256];
        if (unzGetCurrentFileInfo(zipFile, &fileInfo, fileName, sizeof(fileName), NULL, 0, NULL, 0) != UNZ_OK) {
            std::cerr << "Failed to get file info." << std::endl;
            unzClose(zipFile);
            return false;
        }

        // Construct the full output path
        std::string outputPath = outputDir + "\\" + fileName;
        std::string outputDirPath = outputPath.substr(0, outputPath.find_last_of('\\') + 1);

        // Check if the current entry is a directory
        if (fileInfo.uncompressed_size == 0 && fileName[strlen(fileName) - 1] == '/') {
            // Create directory
            if (!std::filesystem::exists(outputPath)) {
                std::filesystem::create_directories(outputPath);
            }
        } else {
            // Create directory if it doesn't exist
            if (!std::filesystem::exists(outputDirPath)) {
                std::filesystem::create_directories(outputDirPath);
            }

            // Open the current file in the zip archive
            if (unzOpenCurrentFile(zipFile) != UNZ_OK) {
                std::cerr << "Failed to open file in zip archive: " << fileName << std::endl;
                unzClose(zipFile);
                return false;
            }

            // Open the output file
            FILE* outFile = fopen(outputPath.c_str(), "wb");
            if (!outFile) {
                std::cerr << "Failed to create output file: " << outputPath << std::endl;
                unzCloseCurrentFile(zipFile);
                unzClose(zipFile);
                return false;
            }

            // Read and write the file content
            char buffer[4096];
            int bytesRead;
            while ((bytesRead = unzReadCurrentFile(zipFile, buffer, sizeof(buffer))) > 0) {
                fwrite(buffer, 1, bytesRead, outFile);
            }

            fclose(outFile);
            unzCloseCurrentFile(zipFile);
        }

        // Move to the next file in the zip archive
        err = unzGoToNextFile(zipFile);
    }

    unzClose(zipFile);
    return true;
}

// 解压 ZIP 数据
bool UnzipData(const std::vector<unsigned char>& zipData, const std::string& outputDir) {
    cerr << "读取中, 共 " << zipData.size() / 1024 / 1024  << "MB" << std::endl;

    // 把 zipData 写进临时文件里:
    std::ofstream wzipFile(TMP_ZIP_FILE, std::ios::binary);
    if (!wzipFile) {
        std::cerr << "Failed to open output file." << std::endl;
        return false;
    }
    wzipFile.write(reinterpret_cast<const char*>(zipData.data()), zipData.size());
    if (!wzipFile) {
        std::cerr << "Failed to write data to file." << std::endl;
        return false;
    }
    wzipFile.close();
    return extractZipFile(TMP_ZIP_FILE, outputDir);
}


bool UnzipEnv(){
    std::vector<unsigned char> zipData;
    if (!LoadEmbeddedZip("ZIPFILE", zipData)) {
        std::cerr << "Failed to load embedded zip file." << std::endl;
        return 1;
    }

    std::string outputDir = target_dir;
    if (!UnzipData(zipData, outputDir)) {
        std::cerr << "Failed to unzip data." << std::endl;
        return 1;
    }
    return 0;
}


bool executePowerShellScript(const std::string& script) {
    // 构造 PowerShell 的命令行参数，并使用 Unicode 宏
    std::string commandLine = "powershell.exe -Command \"" + script + "\"";
    const TCHAR* cmd = (const TCHAR*)commandLine.c_str();

    // 创建进程的启动信息和进程信息
    STARTUPINFO si = { sizeof(si) };
    PROCESS_INFORMATION pi;

    // 创建 PowerShell 进程
    if (!CreateProcess(
        NULL,                   // 程序路径为 NULL，使用命令行中第一个参数
        (LPTSTR)cmd,             // 命令行
        NULL,                   // 不继承进程句柄
        NULL,                   // 不继承线程句柄
        FALSE,                  // 不继承句柄
        0,                      // 进程创建标志
        NULL,                   // 不使用环境变量
        NULL,                   // 使用当前工作目录
        &si,                    // 指向启动信息
        &pi                     // 指向进程信息
    )) {
        std::cerr << "Failed to launch PowerShell: " << GetLastError() << std::endl;
        return false;
    }

    // 等待 PowerShell 进程完成
    WaitForSingleObject(pi.hProcess, INFINITE);

    // 获取 PowerShell 的退出代码
    DWORD exitCode = 0;
    GetExitCodeProcess(pi.hProcess, &exitCode);

    // 关闭进程和线程句柄
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    // 如果退出代码是 0，说明脚本执行成功
    return exitCode == 0;
}
#endif



bool download_win(const string& url) {
    cout << "Trying download via(Windows): " << url << endl;

    #ifdef SD
    cout << "调试中, 默认下载成功..." << endl;
    return true;
    #endif


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
    cout << "Trying download via(Linux): " << url << endl;

    const vector<string> cmds = {
        "wget -O package.zip \"" + url + "\"",
        "curl -L -o package.zip \"" + url + "\""
    };

    for (const auto& cmd : cmds) {
        if (system(cmd.c_str()) == 0 && file_exists("package.zip")) {
            return true;
        }
        system("rm package.zip");
    }
    return false;
}

bool download() {
#ifndef SE
    if (file_exists(target_dir)) {
        cerr << "当前目录存在 ncatbot 文件夹, 请删除后重试" << endl;
        return false;
    }
#else
    cout << "调试解压中, 跳过检查" << endl;
#endif
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

bool rename(string ori, string dst){
    #ifdef _WIN32
    return system(("move " + ori + " " + dst).c_str());
    #else
    return system(("mv " + ori + " " + dst).c_str());
    #endif

}

bool extract() {
    std::cerr << "解压中..." << endl;
#ifndef SE
#ifdef _WIN32
    mkdir(target_dir.c_str());
    if (system("powershell -Command \"Expand-Archive -Path package.zip -DestinationPath ncatbot\"") != 0)
        return false;
#else
    mkdir(target_dir.c_str(), 0777);
    if (system("unzip -q package.zip -d ncatbot") != 0)
        return false;
#endif
#else
    cerr << "调试中, 跳过解压过程" << endl;
#endif

#ifndef SR
    // 重命名package->Python
    if (rename((target_dir + "/package"), (target_dir + "/python")) != 0) {
        perror("Rename failed");
        return false;
    }
#else
    cerr << "调试中, 跳过重命名过程" << endl;
#endif
    cout << "解压成功" << endl;
    return true;
}

void setup_env() {
    rename((target_dir + "/package"), (target_dir + "/python"));
    string success_path = target_dir + "/success.txt";
    ofstream success(success_path);
    success << "success" << endl;
    success.close();
#ifdef _WIN32
    string python_path = target_dir + "\\python\\python.exe";
    cerr << "正在安装 Python 依赖..."
    string cmd = "" + python_path + " -m pip install ncatbot -i https://mirrors.aliyun.com/pypi/simple";
    // cerr << "exec:" << cmd.c_str() << endl;
    system(cmd.c_str());
#else
    string python_path = target_dir + "/python";
    python_path += "/bin/python3";
    string cmd = python_path + " -m pip install ncatbot";
#endif
}

void start_cli(){
    string python_path = target_dir + "\\python\\python.exe";
    string cmd = python_path + " -m ncatbot.cli.main";
    cerr << "exec:" << cmd << endl;
    system(cmd.c_str());
}

bool detect_installed(){
    string success_path = target_dir + "/success.txt";
    return file_exists(success_path);
}

int init(){
    if(!detect_installed()){
        // if (!download()) {
        //     cerr << "All download attempts failed!" << endl;
        //     return 1;
        // }

        // if (!extract()) {
        //     cerr << "Extraction failed!" << endl;
        //     return 1;
        // }
        if (UnzipEnv()){
            cerr << "解压环境失败" << endl;
            return 1;
        }
        remove(TMP_ZIP_FILE.c_str());
        std::cerr << "解压完成" << std::endl;
        setup_env();
    }
    else{
        cerr << "检测到已安装, 跳过下载和安装" << endl;
    }
    start_cli();
    return 0;
}

int main() {
    #ifdef _WIN32
    SetConsoleOutputCP(65001); // 设置控制台输出编码为 UTF-8
    #endif
    std::cout << init() << '\n';
    system("pause");
    return 0;
}
