class RossCli < Formula
  include Language::Python::Virtualenv

  desc "Ross CLI tool"
  homepage "https://github.com/ResearchOS/ross_cli"
  url "https://github.com/ResearchOS/ross_cli/archive/refs/tags/0.1.0.tar.gz"
  sha256 "0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5"  # Replace with actual SHA256
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