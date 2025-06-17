# AudioEditing

This tool allows you to process and organize local music files. It supports various operations such as normalization, renaming, folder structuring, audio processing and more. The aim is to automate audio folder preparation – for example to generate a playlist.

## 1. Install Git (optional)

Git is required if you want to clone the repository. You can install it as follows:

- **Windows**:

  1. Download and install from [https://git-scm.com/downloads](https://git-scm.com/downloads)
  2. During installation, use the default settings.

- **Debian / Ubuntu**:

  ```bash
  sudo apt update
  sudo apt install -y git
  ```

- **Arch Linux**:

  ```bash
  sudo pacman -Syu git
  ```

- **macOS (Homebrew)**:

  ```bash
  brew install git
  ````

Restart your shell and verify:

````bash
git --version
````

## 2. Project Directory Paths

Use one of the following working directory paths depending on how you obtained the project:

**a) With Git**

- **Windows (PowerShell):**
  ```powershell
  C:\Users\<YourUser>\Downloads\AudioEditing
  ```
- **Linux (bash/zsh):**
  ```bash
  /home/<youruser>/Downloads/AudioEditing
  ```
- **macOS (Terminal):**
  ```bash
  /Users/<youruser>/Downloads/AudioEditing
  ```

**b) Without Git (ZIP download)**

After downloading and extracting the ZIP archive, note the `-main` suffix in the folder names:

- **Windows (PowerShell):**
  ```powershell
  C:\Users\<YourUser>\Downloads\AudioEditing-main\AudioEditing-main
  ```
- **Linux (bash/zsh):**
  ```bash
  /home/<youruser>/Downloads/AudioEditing-main/AudioEditing-main
  ```
- **macOS (Terminal):**
  ```bash
  /Users/<youruser>/Downloads/AudioEditing-main/AudioEditing-main
  ```

## 3. Download or Clone the Repository

### a) With Git

```bash
git clone https://github.com/Christoph-Huebner/AudioEditing.git
cd AudioEditing
```

### b) Without Git

1. Download the ZIP archive from: [https://github.com/Christoph-Huebner/AudioEditing](https://github.com/Christoph-Huebner/AudioEditing)
2. Extract the archive.
3. In your terminal, change into the extracted directory:

```bash
cd AudioEditing-main/AudioEditing-main/
```

## 4. Choose Your Setup

From here you can proceed **manually** (without Docker - more difficult) or using **Docker**.

### 4A. Manual Setup (no Docker)

**1. Install Python**

- **Windows**:
  1. Download the installer from https://www.python.org/downloads/
  2. During install, enable:
     - Install pip and py.exe with administrator privileges
     - Add Python to PATH
     - Disable path length limit
  3. Open a new PowerShell and verify:
     ```powershell
     python --version
     pip install --upgrade pip
     ```

- **Debian / Ubuntu**:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-pip
  python3 --version
  pip3 install --upgrade pip
  ```

- **Arch Linux**:
  ```bash
  sudo pacman -Syu python python-pip
  python --version
  pip install --upgrade pip
  ```

- **macOS (Homebrew)**:
  ```bash
  brew install python
  python3 --version
  pip3 install --upgrade pip
  ```

**2. Install FFmpeg**

- **Windows**:
  1. Download the last stable build (not the most recent one) from https://www.gyan.dev/ffmpeg/builds/
  2. Extract (bin, doc, etc.) to `C:\Program Files (x86)\ffmpeg`
  3. Add to PATH in an elevated PowerShell:
     ```powershell
     $env = [Environment]::GetEnvironmentVariable('Path','Machine')
     [Environment]::SetEnvironmentVariable('Path', "$env;C:\Program Files (x86)\ffmpeg\bin", 'Machine')
     ```

- **Debian / Ubuntu**:
  ```bash
  sudo apt update
  sudo apt install -y ffmpeg
  ```

- **Arch Linux**:
  ```bash
  sudo pacman -Syu ffmpeg
  ```

- **macOS (Homebrew)**:
  ```bash
  brew install ffmpeg
  ```

Restart your shell and verify:
```bash
ffmpeg -version
```

**3. Install Python Packages**

In your project directory (see section 2), run with administrative privileges:

- **Debian / Ubuntu & macOS (Homebrew)**:
  ```bash
  pip3 install ffmpeg-python
  ```

- **Windows & Arch Linux**:
  ```bash
  pip install ffmpeg-python
  ```

### 4B. Docker Setup

1. **Install Docker**
   - **Windows (Docker Desktop)**
     https://docs.docker.com/desktop/setup/install/windows-install/
     - Download & install
     - Reboot
     - In Admin PowerShell, add yourself to the Docker group if needed:
       ```powershell
       Add-LocalGroupMember -Group "docker-users" -Member "<YourUser>"
       ```
   - **Debian/Ubuntu**
     https://docs.docker.com/engine/install/debian/
     ```bash
     sudo apt update
     sudo apt install -y ca-certificates curl gnupg lsb-release
     # Add Docker’s GPG key & repository, then:
     sudo apt update
     sudo apt install -y docker-ce docker-ce-cli containerd.io
     sudo usermod -aG docker $USER
     ```
   - **Arch Linux**
     ```bash
     sudo pacman -Syu docker
     sudo systemctl enable --now docker
     sudo usermod -aG docker $USER
     ```
   - **macOS (Docker Desktop)**
     https://docs.docker.com/desktop/setup/install/macos/
     - Install, then ensure Docker Desktop is running.

   After adding your user to the `docker`/`docker-users` group, **log out and log in again** or reboot.

2. **Check Docker**
   Open a new Shell and verify if docker is available:
   ```bash
   docker --version
   ```

3. **Build the Docker Image**
   In the project root:
   ```bash
   docker build -t audioediting:latest .
   ```
   _Note: The first build may take a bit longer to pull base images and install dependencies. This step is required one time, if you don't delete the docker image._

## 5. Test Run

> ⚠️ **IMPORTANT:** The norm command changes the files in the folder directly. Please be careful.

Execute a quick test to confirm everything works. The results shows the renaming of some audio files in simulation mode.

- **Manual (no Docker)**

  - **Debian / Ubuntu & macOS (Homebrew)**:
    ```bash
    python3 main.py --path "<path>" --try-run norm
    ```

  - **Windows & Arch Linux**:
    ```bash
    python main.py --path "<path>" --try-run norm
    ```

- **Docker**
  ```bash
  docker run --rm -v "<host_path>:/app/files" audioediting:latest --path "/app/files" --try-run norm
  ```

## 6. Contribution

1. Fork the repo
2. Create a branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -am "Add feature"`)
4. Push (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 7. License

This project is distributed under a **Non-Commercial** license. See [LICENSE](LICENSE) for details.
