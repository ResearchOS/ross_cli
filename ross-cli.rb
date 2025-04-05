class RossCli < Formula
  include Language::Python::Virtualenv

  desc "Ross CLI tool"
  homepage "https://github.com/ResearchOS/ross_cli"
  url "https://github.com/ResearchOS/ross_cli/ross-0.1.0.tar.gz"
  sha256 "your_package_sha256_here"  # Replace with actual SHA256
  license "MIT"

  depends_on "python@3.9"

  def install
    virtualenv_install_with_resources
  end

  def post_install
    # Create the config directory and file
    system "mkdir", "-p", "#{Dir.home}/.ross"
    
    # Only create config file if it doesn't exist
    unless File.exist?("#{Dir.home}/.ross/ross_config.toml")
      (Dir.home/".ross/ross_config.toml").write <<~EOS
        # Ross default configuration
        [general]
        log = "info"
        
        [index]
      EOS
    end
  end

  test do
    assert_match "Ross", shell_output("#{bin}/ross --help")
  end
end